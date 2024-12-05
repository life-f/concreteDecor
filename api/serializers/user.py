from django.conf import settings
from django.core.mail import send_mail
from djoser.conf import settings as djoser_settings
from djoser.serializers import UserCreatePasswordRetypeSerializer, TokenCreateSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import authenticate, get_user_model

from api.models import CustomUser

User = get_user_model()


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


class CustomTokenCreateSerializer(TokenCreateSerializer):
    def validate(self, attrs):
        password = attrs.get("password")
        params = {djoser_settings.LOGIN_FIELD: attrs.get(djoser_settings.LOGIN_FIELD)}
        self.user = authenticate(
            request=self.context.get("request"), **params, password=password
        )

        if not self.user:
            self.user = User.objects.filter(**params).first()
            if self.user and not self.user.check_password(password):
                self.fail("invalid_credentials")
        if self.user and self.user.is_active:
            return attrs
        if not self.user.is_active:
            send_mail(
                'Код подтверждения регистрации',
                f'Ваш код активации: {self.user.activation_code}',
                settings.DEFAULT_FROM_EMAIL,  # Замените на ваш email отправителя
                [self.user.email],
                fail_silently=False,
            )
            raise ValidationError({"detail": _("Учетная запись не активирована. Пожалуйста, подтвердите вашу почту.")})

        self.fail("invalid_credentials")
