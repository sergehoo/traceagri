from datetime import date
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.db.models.functions import ExtractYear
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from traceagri.api.serializers import ProducteurSerializer, ParcelleMobileSerializer, ProducteurMobileSerializer, \
    UserSerializer, DynamicFormSerializer, ProjectSerializer, CooperativeSerializer, CooperativeMemberSerializer, \
    MobileDataSerializer
from tracelan.models import Producteur, Parcelle, Region, DistrictSanitaire, Cooperative, DynamicForm, FormResponse, \
    FieldResponse, Project, CooperativeMember, MobileData


class DashboardDataAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Nombre total de producteurs
        total_producteurs = Producteur.objects.count()

        # Ventilation des producteurs par sexe
        producteurs_par_sexe = (
            Producteur.objects
            .values('sexe')
            .annotate(count=Count('id'))
        )

        # Ventilation des producteurs par âge
        current_year = date.today().year
        producteurs_par_age = (
            Producteur.objects
            .annotate(age=current_year - ExtractYear('date_naissance'))
            .values('age')
            .annotate(count=Count('id'))
        )

        # Ventilation des producteurs par région
        producteurs_par_region = (
            Producteur.objects
            .values('cooperative__ville__district__region__name')
            .annotate(count=Count('id'))
        )

        # Nombre total de parcelles enregistrées
        total_parcelles = Parcelle.objects.count()

        # Superficie totale des parcelles
        superficie_totale = Parcelle.objects.aggregate(Sum('dimension_ha'))['dimension_ha__sum'] or 0

        # Nombre de coopératives enregistrées
        total_cooperatives = Cooperative.objects.count()

        # Répartition des parcelles par culture (en supposant un champ `culture` dans le modèle `Parcelle`)
        parcelles_par_culture = (
            Parcelle.objects
            .values('culture')
            .annotate(count=Count('id'))
        )

        # Répartition des parcelles par région (avec surface totale et nombre de parcelles)
        parcelles_par_region = (
            DistrictSanitaire.objects
            .values('region__name')
            .annotate(
                total_parcelles=Count('ville__cooperative__producteurs__parcelles', distinct=True),
                surface_totale=Sum('ville__cooperative__producteurs__parcelles__dimension_ha')
            )
            .order_by('-total_parcelles')
        )

        # Surface moyenne des parcelles par producteur
        moyenne_surface_par_producteur = (
                Parcelle.objects.aggregate(
                    avg_surface=Sum('dimension_ha') / Count('producteur', distinct=True)
                )['avg_surface'] or 0
        )

        # Données de retour
        data = {
            'total_producteurs': total_producteurs,
            'producteurs_par_sexe': list(producteurs_par_sexe),
            'producteurs_par_age': list(producteurs_par_age),
            'producteurs_par_region': list(producteurs_par_region),
            'total_parcelles': total_parcelles,
            'superficie_totale': superficie_totale,
            'total_cooperatives': total_cooperatives,
            'parcelles_par_culture': list(parcelles_par_culture),
            'parcelles_par_region': list(parcelles_par_region),
            'moyenne_surface_par_producteur': moyenne_surface_par_producteur,
        }

        return Response(data)


class ProducteurViewSet(viewsets.ModelViewSet):
    queryset = Producteur.objects.all()
    serializer_class = ProducteurSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def search(self, request):
        query = request.query_params.get('q', None)
        if query:
            producteurs = self.queryset.filter(nom__icontains=query)
            serializer = self.get_serializer(producteurs, many=True)
            return Response(serializer.data)
        return Response({"error": "No query provided"}, status=400)


class ParcellesProducteurAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, producteur_id):
        parcelles = Parcelle.objects.filter(producteur_id=producteur_id).values(
            'id', 'nom', 'longitude', 'latitude', 'geojson', 'dimension_ha', 'culture', 'images', 'carracteristic'
        )
        # Construire les URLs complètes des images
        for parcelle in parcelles:
            if parcelle['images']:
                parcelle['images'] = request.build_absolute_uri(settings.MEDIA_URL + parcelle['images'])
            else:
                parcelle['images'] = None  # Gérer le cas où aucune image n'est disponible
        return Response(list(parcelles))


class ParcelleDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, parcelle_id):
        # Récupérer une parcelle spécifique
        parcelle = get_object_or_404(Parcelle, id=parcelle_id)

        # Préparer les données à retourner
        parcelle_data = {
            'id': parcelle.id,
            'nom': parcelle.nom,
            'longitude': parcelle.longitude,
            'latitude': parcelle.latitude,
            'geojson': parcelle.geojson,
            'dimension_ha': parcelle.dimension_ha,
            'culture': parcelle.culture,
            'images': request.build_absolute_uri(parcelle.images.url) if parcelle.images else None,
            'carracteristic': parcelle.carracteristic,
        }

        return Response(parcelle_data)


class ProducteurMobileViewSet(viewsets.ModelViewSet):
    queryset = Producteur.objects.all()
    serializer_class = ProducteurMobileSerializer
    permission_classes = [IsAuthenticated]


class ParcelleMobileViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.all()
    serializer_class = ParcelleMobileSerializer
    permission_classes = [IsAuthenticated]

    def get_producteur_name(self, obj):
        return f"{obj.producteur.nom} {obj.producteur.prenom}" if obj.producteur else "Producteur inconnu"

    def get_localite_name(self, obj):
        return obj.localite.name if obj.localite else "Localité inconnue"


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class DynamicFormViewSet(ReadOnlyModelViewSet):
    queryset = DynamicForm.objects.prefetch_related('fields')
    serializer_class = DynamicFormSerializer
    permission_classes = [IsAuthenticated]


class SubmitFormResponse(APIView):
    def post(self, request, form_id):
        form = get_object_or_404(DynamicForm, pk=form_id)
        response = FormResponse.objects.create(form=form)
        for field in form.fields.all():
            FieldResponse.objects.create(
                response=response,
                field=field,
                value=request.data.get(field.label, "")
            )
        return Response({"message": "Form submitted successfully."}, status=status.HTTP_201_CREATED)


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]


class CooperativeViewSet(ModelViewSet):
    queryset = Cooperative.objects.all()
    serializer_class = CooperativeSerializer


# Vue pour les Membres des Coopératives
class CooperativeMemberViewSet(ModelViewSet):
    queryset = CooperativeMember.objects.prefetch_related('producteurs', 'cooperative')
    serializer_class = CooperativeMemberSerializer


class MobileDataPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class MobileDataStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total = MobileData.objects.count()
        synchronised = MobileData.objects.filter(validate=True).count()
        non_synchronised = total - synchronised

        return Response({
            "total": total,
            "synchronised": synchronised,
            "non_synchronised": non_synchronised
        })


class MobileDataViewSet(viewsets.ModelViewSet):
    """
    API professionnelle pour gérer les données MobileData.
    """
    queryset = MobileData.objects.select_related('localite', 'ville').all()
    serializer_class = MobileDataSerializer
    pagination_class = MobileDataPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['validate', 'created_by']  # Filtres disponibles dans l'API
    search_fields = ['nom', 'prenom', 'telephone']  # Champs pour la recherche textuelle
    ordering_fields = ['created_at', 'updated_at']  # Champs triables
    ordering = ['-created_at']  # Ordre de tri par défaut

    def perform_create(self, serializer):
        """
        Associe automatiquement l'utilisateur connecté lors de la création.
        """
        try:
            serializer.save(created_by=self.request.user)
        except Exception as e:
            raise ValidationError({"error": f"Une erreur est survenue : {str(e)}"})

    def perform_update(self, serializer):
        """
        Associe automatiquement l'utilisateur connecté lors de la mise à jour.
        """
        try:
            serializer.save(updated_by=self.request.user)
        except Exception as e:
            raise ValidationError({"error": f"Une erreur est survenue : {str(e)}"})

    def create(self, request, *args, **kwargs):
        """
        Crée une nouvelle instance MobileData et associe automatiquement l'utilisateur.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Validation des données
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Met à jour une instance existante avec des données validées et associe l'utilisateur.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)  # Validation des données
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """
        Supprime une instance MobileData.
        """
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except Exception as e:
            return Response({"error": f"Erreur lors de la suppression : {str(e)}"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Instance supprimée avec succès"}, status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        """
        Liste les instances MobileData en fonction des filtres, recherche et tri.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """
        Récupère les détails d'une instance spécifique MobileData.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
