from django_unicorn.components import UnicornView

from tracelan.models import Event


class EventListView(UnicornView):
    search_query = ""  # Recherche par nom
    date_filter = ""   # Filtre par date
    events = []        # Liste des événements à afficher

    def mount(self):
        """Initialise la liste des événements."""
        self.events = list(Event.objects.all().order_by("-created_at"))

    def updated_search_query(self):
        """Mise à jour des événements en fonction de la recherche."""
        self.update_events()

    def updated_date_filter(self):
        """Mise à jour des événements en fonction du filtre de date."""
        self.update_events()

    def update_events(self):
        """Mise à jour des événements en fonction des filtres."""
        queryset = Event.objects.all()

        if self.search_query:
            queryset = queryset.filter(name__icontains=self.search_query)

        if self.date_filter:
            queryset = queryset.filter(date=self.date_filter)

        self.events = list(queryset.order_by("-created_at"))
