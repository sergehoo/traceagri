from datetime import date
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.db.models.functions import ExtractYear
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from traceagri.api.serializers import ProducteurSerializer, ParcelleMobileSerializer, ProducteurMobileSerializer, \
    UserSerializer
from tracelan.models import Producteur, Parcelle, Region, DistrictSanitaire, Cooperative


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


class ProducteurMobileViewSet(viewsets.ModelViewSet):
    queryset = Producteur.objects.all()
    serializer_class = ProducteurMobileSerializer
    permission_classes = [IsAuthenticated]


class ParcelleMobileViewSet(viewsets.ModelViewSet):
    queryset = Parcelle.objects.all()
    serializer_class = ParcelleMobileSerializer
    permission_classes = [IsAuthenticated]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer