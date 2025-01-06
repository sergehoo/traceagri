import random
from django.core.management.base import BaseCommand
from faker import Faker

from tracelan.models import Ville, Employee, Project, MobileData


class Command(BaseCommand):
    help = "Génère des données factices pour le modèle MobileData"

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')  # Utilisation de Faker avec un locale français
        villes = Ville.objects.all()
        employees = Employee.objects.all()
        projects = Project.objects.all()

        if not villes.exists() or not employees.exists() or not projects.exists():
            self.stdout.write(
                self.style.ERROR("Assurez-vous que les données pour Ville, Employee et Project existent."))
            return

        # Génération des données factices
        for _ in range(110):  # Nombre d'entrées factices à générer
            ville = random.choice(villes)
            employee = random.choice(employees)
            project = random.choice(projects)

            MobileData.objects.create(
                # Infos Producteur
                nom=fake.last_name(),
                prenom=fake.first_name(),
                sexe=random.choice(['M', 'F']),
                telephone=fake.phone_number(),
                date_naissance=fake.date_of_birth(minimum_age=18, maximum_age=70),
                lieu_naissance=fake.city(),
                photo=None,
                fonction=fake.job(),
                localite=ville,

                # Infos Parcelle
                nom_parcelle=f"Parcelle {fake.word()}",
                dimension_ha=round(random.uniform(0.5, 10), 4),
                longitude=round(random.uniform(-8, -6), 6),
                latitude=round(random.uniform(5, 7), 6),
                images=None,

                # Infos Culture
                type_culture=random.choice(['perennial', 'seasonal']),
                category=random.choice(['vivriere', 'industrial', 'rente', 'maraichere', 'fruitiere', 'specialisee']),
                nom_culture=random.choice(['cacao', 'manioc', 'riz', 'banane']),
                description=fake.text(max_nb_chars=200),
                localite_parcelle=ville,
                annee_mise_en_place=fake.year(),
                date_recolte=fake.date_this_year(),
                date_derniere_recolte=fake.date_this_decade(),
                dernier_rendement_kg_ha=round(random.uniform(500, 2000), 2),
                pratiques_culturales=fake.sentence(),
                utilise_fertilisants=random.choice([True, False]),
                type_fertilisants=fake.word() if random.choice([True, False]) else None,
                analyse_sol=random.choice([True, False]),
                autre_culture=random.choice(['perennial', 'seasonal']),
                autre_culture_nom=random.choice(['coton', 'arachide', 'soja']),
                autre_culture_volume_ha=random.randint(1, 10),

                # Infos Coopérative
                nom_cooperative=fake.company(),
                ville=ville,
                specialites=None,  # À ajuster selon vos besoins
                is_president=random.choice([True, False]),

                projet=project,
                created_by=employee,
            )

        self.stdout.write(self.style.SUCCESS("50 entrées factices ajoutées avec succès."))
