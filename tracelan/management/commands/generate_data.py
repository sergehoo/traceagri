from django.contrib.gis.geos import Point
from faker import Faker
import random
from django.core.management.base import BaseCommand
from tracelan.models import Region, DistrictSanitaire, Ville, Cooperative, Producteur, Parcelle

fake = Faker()


class Command(BaseCommand):
    help = "Génère des données fictives pour les modèles."

    def generate_valid_point(self):
        """Génère un point valide. Réessaie jusqu'à ce qu'un point valide soit obtenu."""
        for _ in range(10):  # Tentatives maximales
            try:
                longitude = random.uniform(-180, 180)  # Générer une longitude valide
                latitude = random.uniform(-90, 90)  # Générer une latitude valide
                return Point(longitude, latitude)
            except Exception as e:
                print(f"Erreur lors de la génération du Point : {e}")
        return None  # Retourne None après plusieurs tentatives

    def handle(self, *args, **kwargs):
        cultures = ['HEVEA', 'CACAO', 'CAFE', 'PALMIER A HUILE', 'ANNARCADE', 'RIZ', 'BLE', 'MAÏS']
        regions = [
            'Bafing',
            'Bagoué',
            'Bélier',
            'Béré',
            'Bounkani',
            'Cavally',
            'Folon',
            'Gbêkê',
            'Gbôklé',
            'Gôh',
            'Grands-Ponts',
            'Guémon',
            'Hambol',
            'Haut-Sassandra',
            'Indénié-Djuablin',
            'Kabadougou',
            'La Mé',
            'Lôh-Djiboua',
            'Marahoué',
            'Montagnes',
            'Moronou',
            'Nawa',
            'Poro',
            'San Pedro',
            'Sud-Comoé',
            'Tchologo',
            'Tonkpi',
            'Worodougou',
            'Yamoussoukro',
            'Yamoussoukro Autonome',
            'Zanzan'
        ]
        districts = [
            'Abidjan',
            'Bas-Sassandra',
            'Comoé',
            'Denguélé',
            'Gôh-Djiboua',
            'Lacs',
            'Lagunes',
            'Montagnes',
            'Sassandra-Marahoué',
            'Savanes',
            'Vallée du Bandama',
            'Woroba',
            'Yamoussoukro',
            'Zanzan'
        ]
        # Générer des régions
        # regions = []
        for _ in range(10):
            region = Region.objects.create(name=random.choice(regions))
            regions.append(region)
        print(f"{len(regions)} régions créées.")

        # Générer des districts sanitaires
        # districts = []
        for _ in range(20):
            try:
                region = random.choice(regions)
                geom = self.generate_valid_point()
                if geom:
                    district = DistrictSanitaire.objects.create(
                        nom=random.choice(districts),
                        region=region,
                        geom=geom
                    )
                    districts.append(district)
                else:
                    print("Impossible de générer un Point valide pour ce district.")
            except Exception as e:
                print(f"Erreur lors de la création du district : {e}")

        if not districts:
            self.stdout.write(self.style.WARNING("Aucun district sanitaire créé. Arrêt du script."))
            return

        print(f"{len(districts)} districts sanitaires créés.")

        # Générer des villes
        villes = []
        for _ in range(50):
            try:
                district = random.choice(districts)
                geom = self.generate_valid_point()
                if geom:
                    ville = Ville.objects.create(
                        name=fake.city(),
                        place=fake.street_name(),
                        population=str(fake.random_int(min=1000, max=100000)),
                        district=district,
                        geom=geom
                    )
                    villes.append(ville)
                else:
                    print("Impossible de générer un Point valide pour cette ville.")
            except Exception as e:
                print(f"Erreur lors de la création de la ville : {e}")

        if not villes:
            self.stdout.write(self.style.WARNING("Aucune ville créée. Arrêt du script."))
            return

        print(f"{len(villes)} villes créées.")

        # Générer des coopératives
        cooperatives = []
        for _ in range(30):
            try:
                ville = random.choice(villes)
                cooperative = Cooperative.objects.create(
                    nom=fake.company(),
                    code=fake.unique.ean(length=8),
                    ville=ville
                )
                cooperatives.append(cooperative)
            except Exception as e:
                print(f"Erreur lors de la création de la coopérative : {e}")

        if not cooperatives:
            self.stdout.write(self.style.WARNING("Aucune coopérative créée. Arrêt du script."))
            return

        print(f"{len(cooperatives)} coopératives créées.")

        # Générer des producteurs
        producteurs = []
        for _ in range(50):
            try:
                cooperative = random.choice(cooperatives)
                producteur = Producteur.objects.create(
                    nom=fake.last_name(),
                    prenom=fake.first_name(),
                    sexe=random.choice(['M', 'F']),
                    telephone=fake.phone_number(),
                    date_naissance=fake.date_of_birth(minimum_age=18, maximum_age=70),
                    lieu_naissance=fake.city(),
                    cooperative=cooperative,
                )
                producteurs.append(producteur)
            except Exception as e:
                print(f"Erreur lors de la création du producteur : {e}")

        if not producteurs:
            self.stdout.write(self.style.WARNING("Aucun producteur créé. Arrêt du script."))
            return

        print(f"{len(producteurs)} producteurs créés.")

        # Générer des parcelles
        for _ in range(200):
            try:
                producteur = random.choice(producteurs)
                localite = random.choice(villes)
                geom = self.generate_valid_point()
                if geom:
                    Parcelle.objects.create(
                        producteur=producteur,
                        code=fake.uuid4(),
                        localite=localite,
                        nom=fake.word(),
                        culture=random.choice(cultures),
                        dimension_ha=fake.random_int(min=1, max=10),
                        geom=geom
                    )
                else:
                    print("Impossible de générer un Point valide pour cette parcelle.")
            except Exception as e:
                print(f"Erreur lors de la création de la parcelle : {e}")

        self.stdout.write(self.style.SUCCESS("200 données générées avec succès !"))
