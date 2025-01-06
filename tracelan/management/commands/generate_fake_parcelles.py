import random
from django.core.management.base import BaseCommand
from faker import Faker
from tracelan.models import Parcelle, Producteur, Ville, Project, Culture, CultureDetail


class Command(BaseCommand):
    help = "Génère des données fictives pour les parcelles avec cultures"

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help="Nombre de parcelles à créer (par défaut : 10)",
        )

    def handle(self, *args, **options):
        count = options['count']
        faker = Faker('fr_FR')

        # Vérifiez qu'il y a des producteurs, villes, projets et cultures disponibles
        producteurs = Producteur.objects.all()
        villes = Ville.objects.all()
        projets = Project.objects.all()
        cultures = Culture.objects.all()

        if not producteurs.exists() or not villes.exists() or not projets.exists() or not cultures.exists():
            self.stdout.write(self.style.ERROR(
                "Assurez-vous que des producteurs, villes, projets et cultures existent dans la base de données."
            ))
            return

        for _ in range(count):
            # Sélectionner des données aléatoires
            producteur = random.choice(producteurs)
            ville = random.choice(villes)
            projet = random.choice(projets)

            # Créer une parcelle fictive
            parcelle = Parcelle(
                producteur=producteur,
                localite=ville,
                projet=projet,
                nom=faker.word().capitalize(),
                code=faker.lexify(text="???-######"),
                dimension_ha=round(random.uniform(0.5, 10), 4),
                status=random.choice(["active", "inactive", "pending"]),
                carracteristic={"type": faker.word(), "soil_quality": random.choice(["good", "average", "poor"])},
                culture={"value": random.choice(cultures.values_list("name", flat=True))},
                affectations=faker.text(max_nb_chars=50),
                longitude=round(random.uniform(-8, -4), 6),
                latitude=round(random.uniform(4, 8), 6),
            )

            # Générer l'identifiant unique
            parcelle.unique_id = parcelle.generate_unique_id()

            # Sauvegarder la parcelle
            parcelle.save()

            # Ajouter des détails de culture
            for _ in range(random.randint(1, 3)):  # Ajouter entre 1 et 3 cultures
                culture = random.choice(cultures)

                culture_detail = CultureDetail(
                    parcelle=parcelle,
                    culture=culture,
                    type_culture=random.choice(["perennial", "seasonal"]),
                    annee_mise_en_place=random.randint(2010, 2023),
                    date_recolte=faker.date_between(start_date='-5y', end_date='today'),
                    date_derniere_recolte=faker.date_between(start_date='-5y', end_date='today'),
                    dernier_rendement_kg_ha=round(random.uniform(500, 5000), 2),
                    pratiques_culturales=faker.text(max_nb_chars=100),
                    utilise_fertilisants=random.choice([True, False]),
                    type_fertilisants=faker.word() if random.choice([True, False]) else None,
                    analyse_sol=random.choice([True, False]),
                )

                # Sauvegarder les détails de culture
                culture_detail.save()

            self.stdout.write(self.style.SUCCESS(f"Parcelle créée avec cultures : {parcelle}"))

        self.stdout.write(self.style.SUCCESS(f"{count} parcelles fictives avec cultures ont été générées avec succès."))
