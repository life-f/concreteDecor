from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


class PromoCode(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Код промокода")
    description = models.TextField(blank=True, verbose_name="Описание промокода")
    discount_amount = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name="Сумма скидки")
    discount_percentage = models.PositiveIntegerField(null=True, blank=True, verbose_name="Процент скидки")
    add_points = models.PositiveIntegerField(null=True, blank=True, verbose_name="Начисление баллов")
    max_usage = models.PositiveIntegerField(default=1, verbose_name="Максимальное количество использований")
    expiration_date = models.DateTimeField(verbose_name="Дата истечения")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    def __str__(self):
        return self.code

    def clean(self):
        """Проверка, что хотя бы одно из полей скидки или баллов заполнено."""
        if not (self.discount_amount or self.discount_percentage or self.add_points):
            raise ValidationError(
                "Необходимо заполнить хотя бы одно из полей: сумма скидки, процент скидки или начисление баллов.")

    def is_usable(self):
        """Проверка, можно ли еще использовать промокод"""
        total_usage = self.usages.count()  # Используем related_name для подсчета использований
        print(total_usage)
        return self.is_active and total_usage < self.max_usage and self.expiration_date > timezone.now()

    class Meta:
        db_table = 'promocode'
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"


User = get_user_model()


class PromoCodeUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь',
                             related_name='promo_code_usages')
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, verbose_name='Промокод', related_name='usages')
    used_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата использования')

    class Meta:
        db_table = 'promocode_usage'
        verbose_name = 'Использование промокода'
        verbose_name_plural = 'Использования промокодов'
        unique_together = ('user', 'promo_code')

    def __str__(self):
        return f'{self.user.email} использовал {self.promo_code.code}'
