from django.contrib.auth.models import User
from rest_framework import serializers
from shapely.geometry import shape

from tracelan.models import Producteur, Parcelle


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