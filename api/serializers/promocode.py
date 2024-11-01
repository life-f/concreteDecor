from rest_framework import serializers
from api.models import PromoCode


class PromoCodeCheckSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)

    def validate_code(self, value):
        try:
            promo_code = PromoCode.objects.get(code=value)
        except PromoCode.DoesNotExist:
            raise serializers.ValidationError("Промокод не найден.")

        # Проверяем, можно ли использовать промокод
        if not promo_code.is_usable():
            raise serializers.ValidationError("Промокод не активен или срок его действия истек.")

        # Проверяем, что хотя бы одно из полей скидки или баллов заполнено
        if not (promo_code.discount_amount or promo_code.discount_percentage or promo_code.add_points):
            raise serializers.ValidationError(
                "Неправильный промокод: не указано ни одно из значений скидки или баллов.")

        return value

    def to_representation(self, instance):
        promo_code = PromoCode.objects.get(code=instance['code'])
        return {
            "code": promo_code.code,
            "discount_amount": promo_code.discount_amount,
            "discount_percentage": promo_code.discount_percentage,
            "add_points": promo_code.add_points,
            "description": promo_code.description,
            "is_active": promo_code.is_active
        }
