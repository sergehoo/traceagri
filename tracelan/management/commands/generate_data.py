import random
from django.core.management.base import BaseCommand
from faker import Faker
from tracelan.models import Region, DistrictSanitaire, Ville, Cooperative, Producteur, Parcelle
from django.contrib.gis.geos import Point

fake = Faker()


class Command(BaseCommand):
    help = "Génère des données fictives pour les modèles."

    def handle(self, *args, **kwargs):
        # Générer des régions
        regions = []
        for _ in range(10):
            region = Region.objects.create(
                name=fake.state(),
            )
            regions.append(region)

        # Générer des districts sanitaires
        districts = []
        for _ in range(20):
            district = DistrictSanitaire.objects.create(
                nom=fake.city(),
                region=random.choice(regions),
                geom=Point(fake.longitude(), fake.latitude())
            )
            districts.append(district)

        # Générer des villes
        villes = []
        for _ in range(50):
            ville = Ville.objects.create(
                name=fake.city(),
                place=fake.street_name(),
                population=str(fake.random_int(min=1000, max=100000)),
                district=random.choice(districts),
                geom=Point(fake.longitude(), fake.latitude())
            )
            villes.append(ville)

        # Générer des coopératives
        cooperatives = []
        for _ in range(30):
            cooperative = Cooperative.objects.create(
                nom=fake.company(),
                code=fake.unique.ean(length=8),
                ville=random.choice(villes)
            )
            cooperatives.append(cooperative)

        # Générer des producteurs
        producteurs = []
        for _ in range(100):
            producteur = Producteur.objects.create(
                nom=fake.last_name(),
                prenom=fake.first_name(),
                sexe=random.choice(['M', 'F']),
                telephone=fake.phone_number(),
                date_naissance=fake.date_of_birth(minimum_age=18, maximum_age=70),
                lieu_naissance=fake.city(),
                cooperative=random.choice(cooperatives),
            )
            producteurs.append(producteur)

        # Générer des parcelles
        for _ in range(200):
            Parcelle.objects.create(
                producteur=random.choice(producteurs),
                code=fake.uuid4(),
                localite=random.choice(villes),
                nom=fake.word(),
                dimension_ha=fake.random_int(min=1, max=10),
                geom=Point(fake.longitude(), fake.latitude())
            )

        self.stdout.write(self.style.SUCCESS("200 données générées avec succès !"))
