import pandas as pd
from django.core.management.base import BaseCommand
from tracelan.models import Cooperative, CooperativeMember, Producteur, Ville


class Command(BaseCommand):
    help = "Importe les producteurs et coopératives depuis un fichier Excel."

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help="Chemin vers le fichier Excel à importer.")

    def handle(self, *args, **kwargs):
        excel_file = kwargs['excel_file']

        # Fonction de normalisation du champ sexe
        def normalize_sexe(value):
            if not value:
                return None
            value = str(value).strip().lower()
            if value in ['m', 'masculin', 'male']:
                return 'M'
            elif value in ['f', 'féminin', 'female']:
                return 'F'
            return None

        try:
            # Chargement du fichier Excel
            data = pd.read_excel(excel_file)

            # Colonnes attendues
            expected_columns = ['nom et prenoms du producteur', 'numero de telephone', 'sexe', 'ville', 'cooperative']
            missing_columns = [col for col in expected_columns if col not in data.columns]

            if missing_columns:
                self.stdout.write(
                    self.style.ERROR(f"Le fichier Excel est invalide. Colonnes manquantes : {', '.join(missing_columns)}")
                )
                return

            for _, row in data.iterrows():
                try:
                    # Extraire les noms et prénoms
                    full_name = str(row['nom et prenoms du producteur']).strip()
                    name_parts = full_name.split(maxsplit=1)
                    nom = name_parts[0]
                    prenom = name_parts[1] if len(name_parts) > 1 else ""

                    # Récupérer ou créer la ville
                    ville_name = str(row['ville']).strip()
                    ville, _ = Ville.objects.get_or_create(name=ville_name)

                    # Récupérer ou créer la coopérative
                    cooperative_name = str(row['cooperative']).strip()
                    cooperative, coop_created = Cooperative.objects.get_or_create(
                        nom=cooperative_name,
                        defaults={'ville': ville}
                    )
                    if coop_created:
                        self.stdout.write(self.style.SUCCESS(f"Coopérative créée : {cooperative_name}"))

                    # Normaliser le sexe
                    sexe = normalize_sexe(row['sexe'])
                    if not sexe:
                        self.stdout.write(self.style.WARNING(f"Sexe invalide pour le producteur : {full_name}. Ligne ignorée."))
                        continue

                    # Récupérer le numéro de téléphone
                    telephone = str(row['numero de telephone']).strip()

                    # Récupérer ou créer le producteur
                    producteur, prod_created = Producteur.objects.get_or_create(
                        nom=nom,
                        prenom=prenom,
                        defaults={
                            'telephone': telephone,
                            'sexe': sexe,
                            'cooperative': cooperative
                        }
                    )
                    if prod_created:
                        self.stdout.write(self.style.SUCCESS(f"Producteur créé : {nom} {prenom}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Producteur existant : {nom} {prenom}. Ignoré."))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Erreur sur la ligne : {row}. Erreur : {e}"))

            self.stdout.write(self.style.SUCCESS("Importation terminée avec succès."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Erreur lors de l'importation : {e}"))