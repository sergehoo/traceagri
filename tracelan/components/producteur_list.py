from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django_unicorn.components import UnicornView

from tracelan.models import Producteur


class ProducteurListView(UnicornView):
    search: str = ""  # Texte de recherche
    producteurs_liste: list = []  # Liste des producteurs sérialisée
    page: int = 1  # Page actuelle
    paginate_by: int = 12  # Nombre d'éléments par page
    total_pages: int = 1  # Nombre total de pages

    def hydrate(self):
        self.filter_producteurs()

    def filter_producteurs(self):
        queryset = Producteur.objects.annotate(
            parcelle_count=Count('parcelles'),
            parcelle_total_dimension=Sum('parcelles__dimension_ha')
        ).order_by('-created_at')

        # Appliquer le filtre de recherche si présent
        if self.search:
            queryset = queryset.filter(
                Q(nom__icontains=self.search) | Q(prenom__icontains=self.search)
            )

        # Pagination
        paginator = Paginator(queryset, self.paginate_by)
        page_obj = paginator.get_page(self.page)

        # Convertir les objets en format sérialisable
        self.producteurs_liste = [
            {
                "id": producteur.id,
                "nom": producteur.nom,
                "prenom": producteur.prenom,
                "photo": producteur.photo.url if producteur.photo else None,
                "telephone": producteur.telephone,
                "cooperative_nom": producteur.cooperative.nom if producteur.cooperative else "Non défini",
                "parcelle_count": producteur.parcelle_count or 0,
                "parcelle_total_dimension": producteur.parcelle_total_dimension or 0,
            }
            for producteur in page_obj.object_list
        ]
        self.total_pages = paginator.num_pages

    def change_page(self, page):
        self.page = page
        self.filter_producteurs()

    def updated(self, name, value):
        """
        Surveille les modifications de la recherche et réinitialise si vide
        """
        if name == "search" and value.strip() == "":
            self.page = 1
            self.filter_producteurs()
