from django.conf import settings
from django.core.mail import send_mail
from djoser.serializers import UserCreatePasswordRetypeSerializer
from rest_framework import serializers

from api.models import CustomUser


class CustomUserCreateSerializer(UserCreatePasswordRetypeSerializer):
    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        model = CustomUser

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['email'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        user.is_active = False  # Отключаем активацию до подтверждения по коду
        user.generate_activation_code()  # Генерация кода
        send_mail(
            'Код подтверждения регистрации',
            f'Ваш код активации: {user.activation_code}',
            settings.DEFAULT_FROM_EMAIL,  # Замените на ваш email отправителя
            [user.email],
            fail_silently=False,
        )
        return user


class CustomUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email', 'phone', 'address', 'gender', 'first_name', 'last_name')
        read_only_fields = ('username',)  # username обновляется автоматически, поэтому делаем его только для чтения

    def update(self, instance, validated_data):
        # Проверяем, изменился ли email
        new_email = validated_data.get('email')
        if new_email and new_email != instance.email:
            # Обновляем username, если email изменился
            instance.username = new_email

        # Обновляем остальные поля
        return super().update(instance, validated_data)
