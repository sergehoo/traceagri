from decimal import Decimal

from django.contrib.auth.models import User

from rest_framework import serializers
from shapely.geometry import shape

from tracelan.models import Producteur, Parcelle, DynamicField, DynamicForm, Project, Ville, Cooperative, \
    CooperativeMember, MobileData


class ProducteurMobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producteur
        fields = '__all__'


class ParcelleMobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcelle
        fields = '__all__'


class ProducteurSerializer(serializers.ModelSerializer):
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = Producteur
        fields = '__all__'  # Inclut tous les champs du modèle

    def get_latitude(self, obj):
        if obj.geojson:
            geometry = shape(obj.geojson['features'][0]['geometry'])
            return geometry.centroid.y  # Latitude
        return None

    def get_longitude(self, obj):
        if obj.geojson:
            geometry = shape(obj.geojson['features'][0]['geometry'])
            return geometry.centroid.x  # Longitude
        return None


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'is_staff']


class DynamicFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicField
        fields = ['label', 'field_type', 'required', 'options', 'order']


class DynamicFormSerializer(serializers.ModelSerializer):
    fields = DynamicFieldSerializer(many=True)

    class Meta:
        model = DynamicForm
        fields = ['id', 'name', 'description', 'fields']


class ProjectSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.ReadOnlyField()
    budget_estimatif = serializers.ReadOnlyField()
    marge_estimatif = serializers.ReadOnlyField()
    profit_percentage = serializers.ReadOnlyField()
    loss_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'description', 'start_date', 'end_date', 'status', 'manager',
            'members', 'parcelles', 'marge_previsionnel', 'previsionnel', 'created_at',
            'updated_at', 'progress_percentage', 'budget_estimatif', 'marge_estimatif',
            'profit_percentage', 'loss_percentage',
        ]


# Sérialiseur pour les Villes
class VilleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ville
        fields = ['id', 'name']  # Ajoutez les champs nécessaires


class CooperativeSerializer(serializers.ModelSerializer):
    president = ProducteurSerializer(read_only=True)
    ville = VilleSerializer(read_only=True)

    class Meta:
        model = Cooperative
        fields = ['id', 'nom', 'code', 'ville', 'president', 'created_at', 'updated_at']


# Sérialiseur pour CooperativeMember
class CooperativeMemberSerializer(serializers.ModelSerializer):
    cooperative = CooperativeSerializer(read_only=True)
    producteurs = ProducteurSerializer(many=True, read_only=True)

    class Meta:
        model = CooperativeMember
        fields = ['id', 'cooperative', 'producteurs', 'created_at', 'updated_at']


class MobileDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileData
        fields = '__all__'

    def validate(self, data):
        # Validation personnalisée pour le téléphone
        if data.get('telephone') and not data['telephone'].isdigit():
            raise serializers.ValidationError(
                {"telephone": "Le numéro de téléphone doit contenir uniquement des chiffres."})
        # if value.size > 5 * 1024 * 1024:  # Limite de 5 MB
        #     raise serializers.ValidationError("L'image est trop volumineuse.")

        # # Validation pour les dimensions de la parcelle
        # if data.get('dimension_ha') and data['dimension_ha'] <= 0:
        #     raise serializers.ValidationError({"dimension_ha": "La dimension doit être supérieure à 0."})

        return data

    def validate_longitude(self, value):
        """
        Vérifie que la longitude est valide (entre -180 et 180) et convertit en Decimal.
        """
        try:
            value = float(value)  # Conversion en float
        except ValueError:
            raise serializers.ValidationError("Longitude invalide. Doit être un nombre.")

        if not (-180 <= value <= 180):
            raise serializers.ValidationError("La longitude doit être comprise entre -180 et 180 degrés.")

        return round(Decimal(value), 6)  # Arrondi à 6 décimales

    def validate_latitude(self, value):
        """
        Vérifie que la latitude est valide (entre -90 et 90) et convertit en Decimal.
        """
        try:
            value = float(value)
        except ValueError:
            raise serializers.ValidationError("Latitude invalide. Doit être un nombre.")

        if not (-90 <= value <= 90):
            raise serializers.ValidationError("La latitude doit être comprise entre -90 et 90 degrés.")

        return round(Decimal(value), 6)  # Arrondi à 6 décimales

    def validate_localite(self, value):
        if not isinstance(value, int):
            raise serializers.ValidationError("La localité doit être une clé primaire (entier).")
        return value

    def validate_photo(self, value):
        if value and not hasattr(value, 'name'):
            raise serializers.ValidationError("Le fichier transmis n'est pas valide.")
        return value


class VilleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ville
        fields = ['id', 'name']  # Incluez les champs nécessaires
