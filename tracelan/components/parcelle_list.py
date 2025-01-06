from django.core.paginator import Paginator
from django.db.models import Q
from django_unicorn.components import UnicornView

from tracelan.models import Cooperative, DistrictSanitaire, Region, Parcelle


# class ParcelleListView(UnicornView):
#     search_query = ""
#     cooperative_id = None
#     district_id = None
#     region_id = None
#     culture = ""
#     parcelles = []
#
#     page = 1
#     total_pages = 1
#     page_numbers = []
#
#     cooperatives = Cooperative.objects.all()
#     districts = DistrictSanitaire.objects.all()
#     regions = Region.objects.all()
#
#     def mount(self):
#         # Initialize the filtered list of parcelles on mount
#         self.filter_parcelles()
#
#     def paginate(self, queryset):
#         paginator = Paginator(queryset, 10)  # 10 parcelles per page
#         page_obj = paginator.get_page(self.page)
#
#         self.total_pages = paginator.num_pages
#
#         # Limit the displayed page numbers to a reasonable range
#         start_page = max(self.page - 2, 1)
#         end_page = min(self.page + 2, self.total_pages)
#         self.page_numbers = list(range(start_page, end_page + 1))
#
#         self.parcelles = page_obj.object_list
#
#     def filter_parcelles(self):
#         # Filter Parcelle objects based on the criteria
#         queryset = Parcelle.objects.select_related('producteur', 'localite', 'localite__district')
#
#         if self.search_query:
#             queryset = queryset.filter(
#                 Q(nom__icontains=self.search_query) |
#                 Q(producteur__nom__icontains=self.search_query) |
#                 Q(producteur__prenom__icontains=self.search_query)
#             )
#
#         if self.cooperative_id:
#             queryset = queryset.filter(producteur__cooperative_id=self.cooperative_id)
#
#         if self.district_id:
#             queryset = queryset.filter(localite__district_id=self.district_id)
#
#         if self.region_id:
#             queryset = queryset.filter(localite__district__region_id=self.region_id)
#
#         if self.culture:
#             queryset = queryset.filter(culture__icontains=self.culture)
#
#         # Apply pagination after filtering
#         self.paginate(queryset)
#
#     def change_page(self, page_number):
#         if 1 <= page_number <= self.total_pages:
#             self.page = page_number
#             self.filter_parcelles()
#
#     def next_page(self):
#         if self.page < self.total_pages:
#             self.page += 1
#             self.filter_parcelles()
#
#     def previous_page(self):
#         if self.page > 1:
#             self.page -= 1
#             self.filter_parcelles()
class ParcelleListView(UnicornView):
    search_query = ""
    cooperative_id = None
    district_id = None
    region_id = None
    culture = ""
    parcelles = []

    page = 1
    total_pages = 1
    page_numbers = []

    cooperatives = Cooperative.objects.all()
    districts = DistrictSanitaire.objects.all()
    regions = Region.objects.all()

    def mount(self):
        # Initialize the filtered list of parcelles on mount
        self.filter_parcelles()

    def paginate(self, queryset):
        paginator = Paginator(queryset, 10)  # 10 parcelles per page
        page_obj = paginator.get_page(self.page)

        self.total_pages = paginator.num_pages

        # Limit the displayed page numbers to a reasonable range
        start_page = max(self.page - 2, 1)
        end_page = min(self.page + 2, self.total_pages)
        self.page_numbers = list(range(start_page, end_page + 1))

        self.parcelles = page_obj.object_list

    def filter_parcelles(self):
        # Filter Parcelle objects based on the criteria
        queryset = Parcelle.objects.select_related('producteur', 'localite', 'localite__district')

        if self.search_query:
            queryset = queryset.filter(
                Q(nom__icontains=self.search_query) |
                Q(producteur__nom__icontains=self.search_query) |
                Q(producteur__prenom__icontains=self.search_query) |
                Q(unique_id__icontains=self.search_query)

            )

        if self.cooperative_id:
            queryset = queryset.filter(producteur__cooperative_id=self.cooperative_id)

        if self.district_id:
            queryset = queryset.filter(localite__district_id=self.district_id)

        if self.region_id:
            queryset = queryset.filter(localite__district__region_id=self.region_id)

        if self.culture:
            queryset = queryset.filter(culture__icontains=self.culture.safe())

        # Apply pagination after filtering
        self.paginate(queryset)

    def updated_search_query(self, value):
        self.page = 1  # Reset to the first page on new search
        self.filter_parcelles()

    def updated_cooperative_id(self, value):
        self.page = 1
        self.filter_parcelles()

    def updated_district_id(self, value):
        self.page = 1
        self.filter_parcelles()

    def updated_region_id(self, value):
        self.page = 1
        self.filter_parcelles()

    def updated_culture(self, value):
        self.page = 1
        self.filter_parcelles()

    def change_page(self, page_number):
        if 1 <= page_number <= self.total_pages:
            self.page = page_number
            self.filter_parcelles()

    def next_page(self):
        if self.page < self.total_pages:
            self.page += 1
            self.filter_parcelles()

    def previous_page(self):
        if self.page > 1:
            self.page -= 1
            self.filter_parcelles()
