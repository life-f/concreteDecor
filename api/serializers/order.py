from rest_framework import serializers
from django.utils import timezone
from urllib3 import request

from api.models import Order, OrderItem, PromoCode, CartItem, Cart, PromoCodeUsage


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']
        depth = 1  # Включает информацию о продукте (например, название)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'shipping_address', 'total_price', 'status', 'created_at', 'delivery_method', 'delivery_cost',
                  'items']


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.CharField()
    promo_code = serializers.CharField(required=False, allow_blank=True)
    use_loyalty_points = serializers.BooleanField(default=False)
    delivery_method = serializers.CharField(required=False)

    def validate_promo_code(self, value):
        if value:
            try:
                promo_code = PromoCode.objects.get(code=value, is_active=True)
                if promo_code.expiration_date < timezone.now():
                    raise serializers.ValidationError("Промокод истек.")
                if not promo_code.is_usable():
                    raise serializers.ValidationError("Промокод больше не доступен для использования.")
                return promo_code
            except PromoCode.DoesNotExist:
                raise serializers.ValidationError("Промокод недействителен.")
        return None

    def calculate_delivery_cost(self, delivery_method):
        if delivery_method == 'standard':
            return 5.00  # фиксированная стоимость стандартной доставки
        elif delivery_method == 'express':
            return 10.00  # фиксированная стоимость экспресс-доставки
        elif delivery_method == 'pickup':
            return 0.00  # самовывоз бесплатный
        return 0.00

    def create_order(self, user, validated_data):
        # Получаем данные из корзины
        cart_items = CartItem.objects.filter(cart__user=user)
        if not cart_items:
            raise serializers.ValidationError("Корзина пуста")

        # Рассчитываем базовую стоимость товаров в корзине
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        # Применяем промокод, если он был введен и валиден
        promo_code = validated_data.get('promo_code')
        discount_amount = 0
        if promo_code:
            if promo_code.discount_amount:
                discount_amount = promo_code.discount_amount
            elif promo_code.discount_percentage:
                discount_amount = total_price * (promo_code.discount_percentage / 100)
            total_price -= discount_amount
        PromoCodeUsage.objects.create(user=user, promo_code=promo_code)

        # Списание бонусных баллов, если указано `use_loyalty_points`
        if validated_data.get('use_loyalty_points') and user.loyalty_points > 0:
            points_to_deduct = min(user.loyalty_points, total_price)
            user.loyalty_points -= points_to_deduct
            total_price -= points_to_deduct
            user.save()

        # Добавляем стоимость доставки
        delivery_cost = self.calculate_delivery_cost(validated_data['delivery_method'])
        total_price = delivery_cost

        # Создаем заказ
        order = Order.objects.create(
            user=user,
            shipping_address=validated_data['shipping_address'],
            total_price=total_price,
            status='pending',
            promo_code=promo_code,
            delivery_method=validated_data['delivery_method'],
            delivery_cost=delivery_cost
        )

        # Копируем товары из корзины в заказ
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price  # Копируем текущую цену
            )

        # Очищаем корзину
        cart_items.delete()
        cart = Cart.objects.filter(user=user)
        cart.delete()

        return order
