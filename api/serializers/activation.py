from rest_framework import serializers

from api.models import CustomUser


class ActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    activation_code = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        activation_code = data.get('activation_code')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Пользователь с данным email не найден.")

        if user.activation_code != activation_code:
            raise serializers.ValidationError("Неверный код активации.")

        return data

    def save(self, **kwargs):
        email = self.validated_data['email']
        user = CustomUser.objects.get(email=email)
        user.is_active = True  # Активация пользователя
        user.activation_code = None  # Сбрасываем код после активации
        user.save()
        return user
