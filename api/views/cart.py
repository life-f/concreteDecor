import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from api.models import Product, Cart, CartItem
from api.serializers import CartItemSerializer, CartItemQuantitySerializer
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
            # Получаем корзину из cookies
            cart_cookie = request.COOKIES.get('cart')
            if cart_cookie:
                cart = json.loads(cart_cookie)
            else:
                cart = {}
            return cart, False  # Возвращаем корзину (dict) и флаг "неавторизованный пользователь"

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
            # Обработка для неавторизованного пользователя (cookies)
            if product_id in cart:
                cart[product_id]['quantity'] += quantity
            else:
                cart[product_id] = {'quantity': quantity}

            # Удаляем товар, если количество <= 0
            if cart[product_id]['quantity'] <= 0:
                del cart[product_id]

            # Обновляем cookies
            response = Response({"cart": cart})
            response.set_cookie('cart', json.dumps(cart), max_age=604800)  # Сохраняем на 7 дней
            return response

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

        else:
            # Обработка для неавторизованного пользователя (cookies)
            cart_items = []
            for product_id, item in cart.items():
                try:
                    product = Product.objects.get(id=product_id)
                    cart_items.append({
                        "product_id": product.id,
                        "name": product.name,
                        "price": product.price,
                        "quantity": item["quantity"]
                    })
                except Product.DoesNotExist:
                    continue  # Игнорируем товары, которых нет в базе данных

            if summary:
                cart_items = [{"product_id": item["product_id"], "quantity": item["quantity"]} for item in cart_items]

            return Response(cart_items, status=status.HTTP_200_OK)
