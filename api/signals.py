from datetime import datetime

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver

from api.models import Cart, CartItem, Product


# @receiver(user_logged_in)
# def transfer_session_cart_to_user_cart(sender, request, user, **kwargs):
#     # Получаем корзину из сессии
#     session_cart = request.session.get("cart", {})
#     if not session_cart:
#         return  # Если корзина пуста, ничего не переносим
#
#     # Получаем или создаем корзину для пользователя
#     cart, created = Cart.objects.get_or_create(user=user)
#     if not created:
#         cart.updated_at = datetime.now()
#         cart.save()
#
#     # Переносим товары из сессионной корзины в корзину пользователя
#     for product_id, item in session_cart.items():
#         try:
#             product = Product.objects.get(id=product_id)
#             cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
#             cart_item.quantity += item["quantity"]
#             cart_item.save()
#         except Product.DoesNotExist:
#             continue  # Игнорируем товары, которых нет в базе данных
#
#     # Очищаем сессионную корзину после переноса
#     request.session["cart"] = {}
#     request.session.modified = True
