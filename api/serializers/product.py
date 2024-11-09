from rest_framework import serializers
from api.models import Product, Category, ProductImage, ProductCharacteristic
from api.serializers.category import CategorySerializer


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['image']


class ProductCharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCharacteristic
        fields = ['key', 'value']


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
