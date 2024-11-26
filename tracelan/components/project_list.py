from django.core.paginator import Paginator
from django.db.models import Q
from django_unicorn.components import UnicornView

from tracelan.models import Project


class ProjectListView(UnicornView):
    search: str = ""  # Variable pour la recherche
    status_filter: str = ""  # Variable pour le filtre par statut
    projects = []  # Liste des projets paginés
    total_projects: int = 0  # Nombre total de projets
    page: int = 1  # Page actuelle
    per_page: int = 10  # Nombre d'éléments par page
    total_pages: int = 1  # Total des pages

    def mount(self):
        """Initialisation des données."""
        self.load_projects()

    def load_projects(self):
        """Charge la liste des projets avec filtres et pagination."""
        query = Q(name__icontains=self.search) | Q(description__icontains=self.search)
        if self.status_filter:
            query &= Q(status=self.status_filter)

        # Charger tous les projets filtrés
        all_projects = Project.objects.filter(query)
        self.total_projects = all_projects.count()

        # Gérer la pagination
        paginator = Paginator(all_projects, self.per_page)
        self.total_pages = paginator.num_pages
        self.page = min(max(1, self.page), self.total_pages)  # S'assurer que la page est valide

        # Charger les projets pour la page actuelle
        self.projects = paginator.get_page(self.page).object_list

    def updated_search(self, value):
        """Met à jour la liste lors de la recherche."""
        self.page = 1  # Retour à la première page
        self.load_projects()

    def updated_status_filter(self, value):
        """Met à jour la liste lorsque le filtre change."""
        self.page = 1  # Retour à la première page
        self.load_projects()

    def change_page(self, page):
        """Changer de page."""
        self.page = page
        self.load_projects()