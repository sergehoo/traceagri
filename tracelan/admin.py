from django.contrib import admin

from tracelan.models import Cooperative, Producteur, Parcelle, Ville, DistrictSanitaire, Region, Project, Task, \
    Milestone, Deliverable, Employee, Depense, Event, EventInvite, DynamicField, \
    DynamicForm, FieldResponse, FormResponse, CultureDetail, Culture, MobileData

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
    list_display = ("nom", "unique_id", "dimension_ha", "producteur", "longitude", "latitude")
    search_fields = ("nom", "producteur__nom", "producteur__prenom","unique_id")
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


# @admin.register(CulturePerennial)
# class CulturePerennialAdmin(admin.ModelAdmin):
#     list_display = (
#         'type_culture', 'parcelle', 'annee_mise_en_place', 'date_derniere_recolte', 'dernier_rendement_kg_ha')
#     list_filter = ('type_culture', 'annee_mise_en_place', 'utilise_fertilisants', 'analyse_sol')
#     search_fields = ('type_culture', 'parcelle__nom')
#     ordering = ('-annee_mise_en_place',)
#
#
# @admin.register(CultureSeasonal)
# class CultureSeasonalAdmin(admin.ModelAdmin):
#     list_display = ('type_culture', 'parcelle', 'annee_mise_en_place', 'date_recolte', 'dernier_rendement_kg_ha')
#     list_filter = ('type_culture', 'annee_mise_en_place', 'utilise_fertilisants', 'analyse_sol')
#     search_fields = ('type_culture', 'parcelle__nom')
#     ordering = ('-annee_mise_en_place',)


# Configuration pour les champs dynamiques

@admin.register(Culture)
class CultureAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'created_at', 'updated_at')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(CultureDetail)
class CultureDetailAdmin(admin.ModelAdmin):
    list_display = (
        'culture', 'type_culture', 'parcelle', 'annee_mise_en_place', 'dernier_rendement_kg_ha', 'utilise_fertilisants')
    list_filter = ('type_culture', 'utilise_fertilisants', 'analyse_sol')
    search_fields = ('culture__name', 'parcelle__nom', 'pratiques_culturales')
    autocomplete_fields = ('culture', 'parcelle')
    fieldsets = (
        (None, {
            'fields': ('parcelle', 'culture', 'type_culture', 'annee_mise_en_place')
        }),
        ('Récoltes', {
            'fields': ('date_recolte', 'date_derniere_recolte', 'dernier_rendement_kg_ha')
        }),
        ('Pratiques agricoles', {
            'fields': ('pratiques_culturales', 'utilise_fertilisants', 'type_fertilisants', 'analyse_sol')
        }),
        ('Informations système', {
            'classes': ('collapse',),
            'fields': ('id',),
        }),
    )
    readonly_fields = ('id',)


class DynamicFieldInline(admin.TabularInline):
    model = DynamicField
    extra = 1  # Nombre de champs supplémentaires visibles par défaut
    fields = ['label', 'field_type', 'required', 'options', 'order']


# Configuration pour les formulaires dynamiques
@admin.register(DynamicForm)
class DynamicFormAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'created_at']
    list_filter = ['project', 'created_at']
    search_fields = ['name', 'project__name']
    inlines = [DynamicFieldInline]


# Configuration pour les réponses de formulaire
class FieldResponseInline(admin.TabularInline):
    model = FieldResponse
    extra = 0  # Ne pas afficher de champs supplémentaires par défaut


@admin.register(FormResponse)
class FormResponseAdmin(admin.ModelAdmin):
    list_display = ['form', 'submitted_at']
    list_filter = ['form', 'submitted_at']
    search_fields = ['form__name']
    inlines = [FieldResponseInline]


@admin.register(MobileData)
class MobileDataAdmin(admin.ModelAdmin):
    # Champs à afficher dans la liste d'administration
    list_display = (
        'projet',
        'nom',
        'prenom',
        'sexe',
        'telephone',
        'nom_parcelle',
        'type_culture',
        'category',
        'nom_culture',
        'annee_mise_en_place',
        'dernier_rendement_kg_ha',
        'nom_cooperative',
        'created_at',
    )
    # Champs cliquables pour accéder aux détails
    list_display_links = ('nom', 'prenom', 'nom_parcelle')
    # Champs de recherche
    search_fields = ('nom', 'prenom', 'telephone', 'nom_parcelle', 'nom_culture')
    # Filtres dans la liste
    list_filter = ('projet', 'sexe', 'category', 'type_culture', 'nom_culture', 'utilise_fertilisants', 'analyse_sol')
    # Champs en lecture seule
    readonly_fields = ('created_at', 'updated_at')
    # Organisation des champs dans le formulaire
    fieldsets = (
        ("Informations sur le Producteur", {
            'fields': (
                'nom', 'prenom', 'sexe', 'telephone', 'date_naissance',
                'lieu_naissance', 'photo', 'fonction', 'localite',
            )
        }),
        ("Informations sur la Parcelle", {
            'fields': (
                'nom_parcelle', 'dimension_ha', 'longitude', 'latitude', 'images',
            )
        }),
        ("Informations sur la Culture", {
            'fields': (
                'type_culture', 'category', 'nom_culture', 'description',
                'localite_parcelle', 'annee_mise_en_place', 'date_recolte',
                'date_derniere_recolte', 'dernier_rendement_kg_ha', 'pratiques_culturales',
                'utilise_fertilisants', 'type_fertilisants', 'analyse_sol',
                'autre_culture', 'autre_culture_nom', 'autre_culture_volume_ha',
            )
        }),
        ("Informations sur la Coopérative", {
            'fields': (
                'nom_cooperative', 'ville', 'specialites', 'is_president',
            )
        }),
        ("Informations Générales", {
            'fields': ('projet', 'created_by', 'created_at', 'updated_at','validate')
        }),
    )
