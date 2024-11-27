import os
import zipfile
import re
from io import BytesIO

from django.contrib.gis.geos import Point
from django.core.management import BaseCommand
from fastkml import kml
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

from tracelan.models import Producteur, Parcelle


class Command(BaseCommand):
    help = "Importe plusieurs fichiers KMZ et crée des parcelles associées aux producteurs."

    def add_arguments(self, parser):
        parser.add_argument(
            "directory",
            type=str,
            help="Chemin du répertoire contenant les fichiers KMZ",
        )

    def handle(self, *args, **options):
        directory_path = options["directory"]

        if not os.path.exists(directory_path):
            self.stdout.write(self.style.ERROR(f"Répertoire introuvable : {directory_path}"))
            return

        for filename in os.listdir(directory_path):
            if filename.endswith(".kmz"):
                file_path = os.path.join(directory_path, filename)
                try:
                    self.import_kmz(file_path, filename)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erreur avec le fichier {filename} : {e}"))

    def clean_name(self, name):
        """
        Nettoie les noms en supprimant les espaces superflus, les accents, et les parenthèses.
        """
        name = re.sub(r'\(.*?\)', '', name)  # Supprime tout ce qui est entre parenthèses
        return " ".join(name.split()).title()  # Supprime les espaces superflus et normalise la casse

    def parse_filename(self, filename):
        """
        Analyse dynamiquement le nom de fichier pour extraire le nom du producteur et le code de la parcelle.
        """
        # Supprimer l'extension .kmz
        base_name = filename.replace(".kmz", "").strip()

        # Séparer les parties du nom par " - "
        try:
            part1, part2 = base_name.split(" - ")
        except ValueError:
            raise ValueError(f"Nom de fichier invalide : {filename}")

        # Identifier lequel est le code de la parcelle et lequel est le nom du producteur
        if part1.startswith("Y") and part1.isalnum():  # Si part1 ressemble à un code de parcelle
            return part1, self.clean_name(part2)
        elif part2.startswith("Y") and part2.isalnum():  # Si part2 ressemble à un code de parcelle
            return part2, self.clean_name(part1)
        else:
            raise ValueError(f"Impossible d'extraire le code de parcelle et le nom du producteur pour : {filename}")

    def find_producteur(self, first_name, last_name):
        """
        Recherche un producteur par nom et prénom, avec gestion des cas spéciaux.
        """
        producteur = Producteur.objects.filter(
            nom__iexact=first_name.strip(),
            prenom__iexact=last_name.strip(),
        ).first()

        if not producteur:
            producteur = Producteur.objects.filter(
                nom__icontains=first_name.strip(),
                prenom__icontains=last_name.strip(),
            ).first()

        if not producteur:
            producteur = Producteur.objects.filter(
                nom__iexact=last_name.strip(),
                prenom__iexact=first_name.strip(),
            ).first()

        if not producteur:
            producteur = Producteur.objects.filter(
                nom__icontains=first_name.strip()
            ).first()

        return producteur

    def import_kmz(self, file_path, filename):
        """
        Importe un fichier KMZ et crée ou met à jour une parcelle.
        """
        try:
            # Extraire le code de la parcelle et le nom du producteur
            parcel_code, producer_name = self.parse_filename(filename)
        except ValueError as e:
            self.stdout.write(self.style.WARNING(str(e)))
            return

        try:
            first_name, last_name = producer_name.split(" ", 1)
        except ValueError:
            self.stdout.write(self.style.WARNING(f"Format du nom du producteur invalide dans le fichier : {filename}."))
            return

        self.stdout.write(f"Recherche du producteur avec nom: {first_name}, prénom: {last_name}")

        producteur = self.find_producteur(first_name, last_name)

        if not producteur:
            self.stdout.write(self.style.WARNING(f"Producteur {producer_name} non trouvé. Ignoré."))
            return

        with open(file_path, "rb") as kmz_file:
            geojson_data, dimension_ha, centroid = self.process_kmz(kmz_file)

            parcelle_nom = f"Parcelle {producer_name}"

            parcelle, created = Parcelle.objects.update_or_create(
                producteur=producteur,
                code=parcel_code,
                defaults={
                    "nom": parcelle_nom,
                    "geojson": geojson_data,
                    "dimension_ha": dimension_ha,
                    "longitude": centroid.x,
                    "latitude": centroid.y,
                    "geom": Point(centroid.x, centroid.y, srid=4326),
                },
            )
            action = "Créée" if created else "Mise à jour"
            self.stdout.write(self.style.SUCCESS(f"{action}: {parcelle.nom} pour {producteur.nom} {producteur.prenom}"))

    def process_kmz(self, kmz_file):
        """
        Convertit un fichier KMZ en GeoJSON et extrait la surface et le centroid.
        """
        try:
            with zipfile.ZipFile(BytesIO(kmz_file.read())) as kmz:
                kml_file = [f for f in kmz.namelist() if f.endswith(".kml")][0]
                with kmz.open(kml_file, "r") as kml_content:
                    kml_content = kml_content.read().decode("utf-8")
                    k = kml.KML()
                    k.from_string(kml_content)

                    geojson_features = []
                    self.extract_features(k.features(), geojson_features)

                    geometries = [shape(feature["geometry"]) for feature in geojson_features]
                    combined_geometry = unary_union(geometries)

                    dimension_ha = combined_geometry.area / 10000
                    centroid = combined_geometry.centroid

                    geojson_data = {
                        "type": "FeatureCollection",
                        "features": geojson_features,
                    }

                    return geojson_data, round(dimension_ha, 4), centroid
        except Exception as e:
            raise ValueError(f"Erreur lors du traitement du fichier KMZ : {e}")

    def extract_features(self, features, geojson_features):
        """
        Récupère les géométries des fonctionnalités dans le KML.
        """
        for feature in features:
            if hasattr(feature, "geometry") and feature.geometry:
                geojson_features.append({
                    "type": "Feature",
                    "geometry": mapping(feature.geometry),
                    "properties": {"name": feature.name},
                })
            if hasattr(feature, "features"):
                self.extract_features(feature.features(), geojson_features)