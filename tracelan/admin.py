from django.contrib import admin

from tracelan.models import Cooperative, Producteur, Parcelle, Ville, DistrictSanitaire, Region, Project, Task, \
    Milestone, Deliverable, Employee, Depense, Event, EventInvite

admin.site.site_header = 'TRACAFRIC BACK-END CONTROLER'
admin.site.site_title = 'TRACAFRIC Super Admin Pannel'
admin.site.site_url = 'http://TRACAFRIC.com/'
admin.site.index_title = 'TRACAFRIC'
admin.empty_value_display = '**Empty**'


# Register your models here.
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(DistrictSanitaire)
class DistrictSanitaireAdmin(admin.ModelAdmin):
    list_display = ("nom", "region", "geom")
    search_fields = ("nom", "region__name")
    list_filter = ("region",)


@admin.register(Ville)
class VilleAdmin(admin.ModelAdmin):
    list_display = ("name", "place", "population", "district")
    search_fields = ("name", "district__nom")
    list_filter = ("district",)


@admin.register(Cooperative)
class CooperativeAdmin(admin.ModelAdmin):
    list_display = ("nom", "code", "ville")
    search_fields = ("nom", "code", "ville__name")
    list_filter = ("ville",)


@admin.register(Producteur)
class ProducteurAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "sexe", "telephone", "cooperative")
    search_fields = ("nom", "prenom", "cooperative__nom")
    list_filter = ("sexe", "cooperative")


@admin.register(Parcelle)
class ParcelleAdmin(admin.ModelAdmin):
    list_display = ("nom", "dimension_ha", "producteur", "longitude", "latitude")
    search_fields = ("nom", "producteur__nom", "producteur__prenom")
    list_filter = ("producteur",)
    readonly_fields = ("longitude", "latitude")

    default_lat = 7.539989  # Latitude de la Côte d'Ivoire
    default_lon = -5.54708  # Longitude de la Côte d'Ivoire
    default_zoom = 7


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "manager", "start_date", "end_date", "status", "created_at")
    list_filter = ("status", "manager", "start_date")
    search_fields = ("name", "description")
    ordering = ("-created_at",)
    filter_horizontal = ("members",)  # Pour faciliter la gestion des membres


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "priority", "status", "assigned_to", "due_date", "created_at")
    list_filter = ("priority", "status", "project", "assigned_to")
    search_fields = ("name", "description")
    ordering = ("-created_at",)


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "due_date", "is_completed", "created_at")
    list_filter = ("is_completed", "project")
    search_fields = ("name", "description")
    ordering = ("-created_at",)


@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ("projet", "categorie", "montant")
    # list_filter = ("categorie")
    # search_fields = "projet"
    # ordering = ("-created_at",)


@admin.register(Deliverable)
class DeliverableAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "is_approved", "submitted_at", "approved_at")
    list_filter = ("is_approved", "project")
    search_fields = ("name", "description")
    ordering = ("-submitted_at",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("user", "qlook_id")
    list_filter = ("job_title",)
    search_fields = ("name", "description")
    ordering = ("-created_at",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "location")

@admin.register(EventInvite)
class EventInviteAdmin(admin.ModelAdmin):
    list_display = ('event', 'get_invite', 'invite_type_display', 'created_at', 'updated_at')
    list_filter = ('invite_type',)  # Add filters for invite type
    search_fields = ('event__name', 'invite_id')  # Search by event name or invite ID

    def invite_type_display(self, obj):
        """
        Display the human-readable name for the invite type.
        """
        return obj.get_invite_type_display()
    invite_type_display.short_description = "Type d'invité"

    def get_invite(self, obj):
        """
        Display the related invite object name.
        """
        try:
            return obj.get_invite()
        except Exception:
            return "Not Found"
    get_invite.short_description = "Nom de l'invité"
