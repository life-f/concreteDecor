import datetime

from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Cart, CartItem, Product
from api.serializers import CartItemSerializer, CartItemQuantitySerializer


class CartView(APIView):
    """
    API для работы с корзиной, поддерживает авторизованных и неавторизованных пользователей.
    """

    def get_cart_for_user(self, request):
        """Возвращает корзину для авторизованного пользователя или корзину сессии для неавторизованного."""
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
            if not created:
                cart.updated_at = datetime.datetime.now()
                cart.save()
            return cart, True  # Возвращаем флаг для указания, что корзина привязана к пользователю
        else:
            session_cart = request.session.get("cart", {})
            return session_cart, False  # Возвращаем флаг для сессионной корзины

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

        # Определяем корзину (для авторизованного пользователя или для сессии)
        cart, is_user_cart = self.get_cart_for_user(request)

        if is_user_cart:
            # Обработка для авторизованного пользователя
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if not created:
                if cart_item.quantity + quantity > 0:
                    cart_item.quantity += quantity
                else:
                    cart_item.quantity = 0
            else:
                cart_item.quantity = quantity
            if cart_item.quantity > 0:
                cart_item.save()
            else:
                cart_item.delete()
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Обработка для неавторизованного пользователя (сессионная корзина)
            if product_id in cart:
                if cart[product_id]["quantity"] + quantity > 0:
                    cart[product_id]["quantity"] += quantity
                else:
                    cart[product_id]["quantity"] = 0
            else:
                cart[product_id] = {"quantity": quantity}
            if cart[product_id]["quantity"] == 0:
                del cart[product_id]
            request.session["cart"] = cart
            request.session.modified = True
            serializer = {"product_id": product_id, "quantity": cart[product_id]["quantity"]}
        return Response(serializer, status=status.HTTP_200_OK)

    def get(self, request):
        """
        Получает товары в корзине.
        Если передан параметр `summary=true`, возвращает сокращенный список с ID и количеством.
        """
        summary = request.query_params.get("summary", "false").lower() == "true"

        # Определяем корзину (для авторизованного пользователя или для сессии)
        cart, is_user_cart = self.get_cart_for_user(request)

        if is_user_cart:
            # Обработка для авторизованного пользователя
            items = cart.items.all()
            serializer_class = CartItemQuantitySerializer if summary else CartItemSerializer
            serializer = serializer_class(items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            # Обработка для неавторизованного пользователя (сессионная корзина)
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

# class CartItemsSummaryView(generics.ListAPIView):
#     """Сокращенный список товаров в корзине: только ID позиции и количество"""
#     serializer_class = CartItemQuantitySerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         cart, created = Cart.objects.get_or_create(user=self.request.user)
#         return cart.items.all()
#
#
# class AddToCartView(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def post(self, request):
#         product_id = request.data.get("product_id")
#         quantity = request.data.get("quantity", 1)
#
#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return Response({"error": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND)
#
#         # Получаем корзину пользователя, создаем новую, если ее нет
#         cart, created = Cart.objects.get_or_create(user=request.user)
#
#         # Проверяем, есть ли товар уже в корзине
#         cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
#         if not created:
#             # Если товар уже есть в корзине, увеличиваем количество
#             cart_item.quantity += int(quantity)
#         else:
#             # Если это новый товар, задаем количество
#             cart_item.quantity = int(quantity)
#         cart_item.save()
#
#         serializer = CartItemSerializer(cart_item)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# class SessionCartView(APIView):
#     """
#     API для добавления товара в корзину и получения корзины из сессии.
#     """
#
#     def post(self, request):
#         # Получаем ID товара и количество
#         product_id = str(request.data.get("product_id"))
#         quantity = int(request.data.get("quantity", 1))
#
#         # Проверка существования товара
#         try:
#             product = Product.objects.get(id=product_id)
#         except Product.DoesNotExist:
#             return Response({"error": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND)
#
#         # Получаем корзину из сессии или создаем новую
#         cart = request.session.get("cart", {})
#
#         # Если товар уже есть в корзине, увеличиваем количество
#         if product_id in cart:
#             cart[product_id]["quantity"] += quantity
#         else:
#             # Если товара нет в корзине, добавляем его
#             cart[product_id] = {"quantity": quantity}
#
#         # Сохраняем корзину в сессии
#         request.session["cart"] = cart
#         request.session.modified = True
#
#         return Response({"message": "Товар добавлен в корзину", "cart": cart}, status=status.HTTP_200_OK)
#
#     def get(self, request):
#         # Получаем корзину из сессии
#         cart = request.session.get("cart", {})
#         cart_items = []
#
#         # Составляем полные данные о товарах из корзины
#         for product_id, item in cart.items():
#             try:
#                 product = Product.objects.get(id=product_id)
#                 cart_items.append({
#                     "product_id": product.id,
#                     "name": product.name,
#                     "price": product.price,
#                     "quantity": item["quantity"]
#                 })
#             except Product.DoesNotExist:
#                 continue  # Игнорируем товары, которых нет в базе данных
#
#         return Response({"cart_items": cart_items}, status=status.HTTP_200_OK)
