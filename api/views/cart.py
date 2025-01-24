import datetime

from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from api.models import Product, Cart, CartItem, PromoCode
from api.serializers import CartItemSerializer, CartItemQuantitySerializer, OrderCreateSerializer
import json


class CartView(APIView):
    """
    API для работы с корзиной, поддерживает авторизованных и неавторизованных пользователей.
    """

    def get_cart_for_user(self, request):
        """Возвращает корзину для авторизованного пользователя или корзину из cookies для неавторизованного."""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            if not created:
                cart.updated_at = datetime.datetime.now()
                cart.save()
            return cart, True  # Возвращаем корзину и флаг "авторизованный пользователь"
        else:
            return {}, False

    def post(self, request):
        """
        Добавляет товар в корзину.
        """
        product_id = str(request.data.get("product_id"))
        quantity = int(request.data.get("quantity", 1))

        # Проверяем наличие товара
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Определяем корзину (авторизованный или неавторизованный пользователь)
        cart, is_user_cart = self.get_cart_for_user(request)

        if is_user_cart:
            # Обработка для авторизованного пользователя
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                cart_item.quantity += quantity
            else:
                cart_item.quantity = quantity

            if cart_item.quantity > 0:
                cart_item.save()
            else:
                cart_item.delete()

            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("Пользователь не авторизован", status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        Получает товары в корзине.
        Если передан параметр `summary=true`, возвращает сокращенный список с ID и количеством.
        """
        summary = request.query_params.get("summary", "false").lower() == "true"

        # Определяем корзину (авторизованный или неавторизованный пользователь)
        cart, is_user_cart = self.get_cart_for_user(request)

        if is_user_cart:
            # Обработка для авторизованного пользователя
            items = cart.items.all()
            serializer_class = CartItemQuantitySerializer if summary else CartItemSerializer
            serializer = serializer_class(items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({}, status=status.HTTP_200_OK)


class CartTotalSum(APIView):
    """API для получения стоимости корзины"""

    def post(self, request):
        total = 0
        cart, is_user_cart = CartView.get_cart_for_user(CartView(), request)
        if is_user_cart:
            cart_items = CartItem.objects.filter(cart__user=request.user)
            total = sum(item.product.price * item.quantity for item in cart_items)
        if not is_user_cart:
            cart = json.loads(request.data['cart'])
            total = sum(item.product.price * item.quantity for item in cart)
        total += OrderCreateSerializer.calculate_delivery_cost(OrderCreateSerializer(), '')
        if 'promocode' in request.data and request.data['promocode']:
            promo_code = PromoCode.objects.get(code=request.data['promocode'], is_active=True)
            discount_amount = 0
            if promo_code:
                if promo_code.discount_amount:
                    discount_amount = promo_code.discount_amount
                elif promo_code.discount_percentage:
                    discount_amount = total * (promo_code.discount_percentage / 100)
            total -= float(discount_amount)
        if total < 0:
            total = 0
        return Response({"total": total}, status=status.HTTP_200_OK)
