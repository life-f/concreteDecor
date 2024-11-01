from rest_framework import serializers
from api.models import Product, Category, ProductImage
from api.serializers.category import CategorySerializer


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    images = ImageSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'category', 'images']
