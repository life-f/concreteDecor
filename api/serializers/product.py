from rest_framework import serializers

from api.models import Product, ProductImage, ProductCharacteristic
from api.serializers.category import CategorySerializer


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']


class ProductCharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCharacteristic
        fields = ['key', 'value']


class ProductNameImageSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'images']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    images = ImageSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'stock', 'category', 'images']


class ProductFullSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many=True)
    images = ImageSerializer(many=True)
    characteristics = ProductCharacteristicSerializer(many=True)

    class Meta:
        model = Product
        fields = '__all__'


class ProductForSeriesSerializer(serializers.ModelSerializer):
    """Сериализатор для серий товаров"""
    images = ImageSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'color', 'images']
