import pandas as pd
from django.core.management.base import BaseCommand
from tracelan.models import Region, DistrictSanitaire, Ville


class Command(BaseCommand):
    help = "Importe les localités de Côte d'Ivoire depuis un fichier Excel."

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help="Chemin vers le fichier Excel à importer.")

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']

        try:
            # Chargement du fichier Excel
            data = pd.read_excel(excel_file)

            # Normaliser les colonnes pour éviter les problèmes de casse ou d'espaces
            data.columns = data.columns.str.strip().str.lower()

            # Afficher les colonnes détectées (pour debug)
            print("Colonnes détectées :", data.columns.tolist())

            # Vérification des colonnes nécessaires
            required_columns = ['ville', 'district', 'region']
            missing_columns = [col for col in required_columns if col not in data.columns]
            if missing_columns:
                self.stdout.write(
                    self.style.ERROR(f"Le fichier Excel est invalide. Colonnes manquantes : {', '.join(missing_columns)}")
                )
                return

            # Traitement des données (comme dans le script précédent)
            regions_cache = {region.name: region for region in Region.objects.all()}
            districts_cache = {
                (district.nom, district.region_id): district
                for district in DistrictSanitaire.objects.all()
            }
            villes_cache = {
                (ville.name, ville.district_id): ville
                for ville in Ville.objects.all()
            }

            for _, row in data.iterrows():
                region_name = row['region']
                district_name = row['district']
                ville_name = row['ville']

                # Création ou récupération de la région
                if region_name not in regions_cache:
                    region, created = Region.objects.get_or_create(name=region_name)
                    regions_cache[region_name] = region
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Région créée : {region_name}"))
                else:
                    region = regions_cache[region_name]

                # Création ou récupération du district
                district_key = (district_name, region.id)
                if district_key not in districts_cache:
                    district, created = DistrictSanitaire.objects.get_or_create(
                        nom=district_name,
                        region=region
                    )
                    districts_cache[district_key] = district
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"District créé : {district_name}"))
                else:
                    district = districts_cache[district_key]

                # Création ou récupération de la ville
                ville_key = (ville_name, district.id)
                if ville_key not in villes_cache:
                    ville, created = Ville.objects.get_or_create(
                        name=ville_name,
                        district=district
                    )
                    villes_cache[ville_key] = ville
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Ville créée : {ville_name}"))
                else:
                    ville = villes_cache[ville_key]

            self.stdout.write(self.style.SUCCESS("Importation terminée avec succès."))

        except pd.errors.EmptyDataError:
            self.stdout.write(self.style.ERROR("Le fichier Excel est vide ou invalide."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de l'importation : {e}"))
