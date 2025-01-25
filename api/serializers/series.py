from rest_framework import serializers
from api.models import Series
from api.serializers import ProductNameImageSerializer, ProductForSeriesSerializer


class SeriesSerializer(serializers.ModelSerializer):
    products = ProductForSeriesSerializer(many=True, read_only=True)

    class Meta:
        model = Series
        fields = ['id', 'name', 'products']

class SeriesProductListSerializer(serializers.ModelSerializer):
    products = ProductNameImageSerializer(many=True, read_only=True)

    class Meta:
        model = Series
        fields = ['id', 'name', 'products']
