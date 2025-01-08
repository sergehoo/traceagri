from django.core.management import BaseCommand

from tracelan.models import Culture


class Command(BaseCommand):
    help = "Charge une centaine de cultures ivoiriennes dans la base de données"

    def handle(self, *args, **kwargs):
        # Liste de cultures ivoiriennes à ajouter
        cultures_data = [
            {"name": "Maïs", "category": "vivriere", "description": "Culture vivrière populaire en Côte d'Ivoire."},
            {"name": "Manioc", "category": "vivriere", "description": "Source majeure de féculents."},
            {"name": "Riz", "category": "vivriere",
             "description": "Culture vivrière essentielle pour la consommation."},
            {"name": "Cacao", "category": "rente", "description": "Principale culture de rente en Côte d'Ivoire."},
            {"name": "Café", "category": "rente", "description": "Culture de rente historique pour l'économie."},
            {"name": "Ananas", "category": "fruitiere",
             "description": "Produit pour la consommation locale et l'export."},
            {"name": "Banane Plantain", "category": "vivriere",
             "description": "Féculent prisé pour la cuisine locale."},
            {"name": "Mangue", "category": "fruitiere", "description": "Fruit tropical largement cultivé."},
            {"name": "Tomate", "category": "maraichere", "description": "Culture maraîchère populaire."},
            {"name": "Piment", "category": "maraichere", "description": "Ingrédient clé dans de nombreuses recettes."},
            {"name": "Hévéa", "category": "rente", "description": "Source de caoutchouc naturel."},
            {"name": "Palmier à Huile", "category": "rente",
             "description": "Culture pour la production d'huile de palme."},
            {"name": "Coton", "category": "rente", "description": "Culture utilisée pour la production textile."},
            {"name": "Igname", "category": "vivriere",
             "description": "Tubercule consommé dans de nombreux plats locaux."},
            {"name": "Patate Douce", "category": "vivriere", "description": "Tubercule apprécié pour sa douceur."},
            {"name": "Oignon", "category": "maraichere",
             "description": "Culture maraîchère essentielle pour la cuisine."},
            {"name": "Chou", "category": "maraichere", "description": "Légume cultivé pour la consommation locale."},
            {"name": "Carotte", "category": "maraichere", "description": "Légume racine populaire et nutritif."},
            {"name": "Gingembre", "category": "specialisee",
             "description": "Épice utilisée pour la cuisine et les remèdes traditionnels."},
            {"name": "Poivre", "category": "specialisee",
             "description": "Épice largement utilisée dans la cuisine ivoirienne."},
            {"name": "Papaye", "category": "fruitiere", "description": "Fruit tropical prisé pour sa douceur."},
            {"name": "Avocat", "category": "fruitiere",
             "description": "Fruit riche en graisses saines, populaire localement."},
            {"name": "Citron", "category": "fruitiere",
             "description": "Fruit acide utilisé pour les jus et les assaisonnements."},
            {"name": "Pastèque", "category": "fruitiere",
             "description": "Fruit rafraîchissant consommé pendant la saison chaude."},
            {"name": "Melon", "category": "fruitiere",
             "description": "Fruit juteux cultivé pour la consommation locale."},
            {"name": "Poivron", "category": "maraichere",
             "description": "Légume utilisé dans diverses recettes locales."},
            {"name": "Aubergine", "category": "maraichere",
             "description": "Légume populaire dans la cuisine ivoirienne."},
            {"name": "Courgette", "category": "maraichere",
             "description": "Légume polyvalent utilisé dans de nombreux plats."},
            {"name": "Eucalyptus", "category": "specialisee",
             "description": "Plante cultivée pour ses propriétés médicinales et industrielles."},
            {"name": "Baobab", "category": "specialisee",
             "description": "Arbre dont les fruits et feuilles sont utilisés localement."},
            {"name": "Sésame", "category": "specialisee",
             "description": "Graines utilisées dans la cuisine et pour l'huile."},
            {"name": "Taro", "category": "vivriere", "description": "Tubercule consommé dans les régions rurales."},
            {"name": "Canne à Sucre", "category": "rente", "description": "Cultivée pour la production de sucre."},
            {"name": "Gombo", "category": "maraichere",
             "description": "Légume mucilagineux utilisé dans de nombreux plats locaux."},
            {"name": "Araignée de Mer", "category": "emergente",
             "description": "Culture innovante pour des usages spécifiques."},
            {"name": "Mangrove", "category": "emergente", "description": "Utilisée pour des initiatives écologiques."},
            {"name": "Fleurs d'Hibiscus", "category": "florale",
             "description": "Cultivée pour les boissons et l'ornementation."},
            {"name": "Orchidées", "category": "florale", "description": "Fleurs populaires pour l'ornementation."},
            {"name": "Rose", "category": "florale", "description": "Cultivée pour les bouquets et les jardins."},
            {"name": "Céleri", "category": "maraichere",
             "description": "Légume-feuille utilisé comme condiment ou ingrédient principal."},

            # Ajouter autant de cultures que nécessaire...
        ]

        # Ajouter chaque culture dans la base de données
        for culture_data in cultures_data:
            culture, created = Culture.objects.get_or_create(
                name=culture_data["name"],
                category=culture_data["category"],
                defaults={"description": culture_data["description"], "is_active": True}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Culture ajoutée : {culture.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Culture déjà existante : {culture.name}'))

        self.stdout.write(self.style.SUCCESS("Chargement des cultures terminé."))