import random

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name="Email Address")
    phone = models.CharField(max_length=20, unique=True, verbose_name="Телефон", null=True)
    address = models.TextField(blank=True, verbose_name="Адрес", null=True)
    gender = models.PositiveSmallIntegerField(choices=[(1, 'Мужской'), (2, 'Женский')], verbose_name="Пол", null=True,
                                              blank=True)
    loyalty_points = models.PositiveIntegerField(default=0, verbose_name="Бонусные баллы")
    groups = models.ManyToManyField('auth.Group', related_name='customuser_groups', verbose_name='Группы', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='customuser_permissions',
                                              verbose_name='Права пользователя', blank=True)
    activation_code = models.CharField(max_length=6, blank=True, null=True)  # Код активации

    def generate_activation_code(self):
        """Генерация шестизначного кода активации"""
        self.activation_code = str(random.randint(100000, 999999))
        self.save()

    def __str__(self):
        return self.first_name + " " + self.last_name + " (" + self.email + ")"

    class Meta:
        db_table = 'custom_user'
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
