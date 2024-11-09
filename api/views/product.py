from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Product
from api.serializers import ProductSerializer, ProductFullSerializer


class ProductCatalogView(APIView):
    """
    APIView для получения полного каталога товаров,
    с возможностью сортировки, фильтрации по категориям и поиска.
    Получение товара по его id.
    """
    permission_classes = [AllowAny]

    def get(self, request, id=None):
        if id:
            # Если передан `id`, получаем конкретный товар
            product = get_object_or_404(Product, id=id)
            serializer = ProductFullSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Получаем параметры запроса для фильтрации, сортировки и поиска
        category_id = request.query_params.get('category')
        sort_by = request.query_params.get('sort_by')
        search_query = request.query_params.get('search')

        # Начинаем с выборки всех товаров
        products = Product.objects.all()

        # Фильтрация по категории, если передан параметр `category`
        if category_id:
            products = products.filter(category__id=category_id)

        # Поиск по названию и описанию, если передан параметр `search`
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query)
            )

        # Сортировка, если передан параметр `sort_by`
        if sort_by:
            products = products.order_by(sort_by)

        # Сериализация и возврат данных
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
