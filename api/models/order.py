from django.db import models

from api.models.product import Product
from api.models.user import CustomUser


class Order(models.Model):
    STATUS_CHOICES = [
        ('awaiting_pay', 'Ожидает оплаты'),
        ('pending', 'В ожидании'),
        ('confirmed', 'Подтвержден'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('finished', 'Завершен'),
        ('canceled', 'Отменен'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='Пользователь', related_name='orders')
    shipping_address = models.TextField(verbose_name='Адрес доставки')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='awaiting_pay', verbose_name='Статус заказа')
    promo_code = models.ForeignKey('PromoCode', on_delete=models.SET_NULL, null=True, blank=True,
                                   verbose_name='Промокод')
    delivery_method = models.CharField(max_length=20, default='Самовывоз', verbose_name='Способ доставки')
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Стоимость доставки')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        db_table = 'order'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return f'Заказ {self.id} от {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена за единицу')

    class Meta:
        db_table = 'order_item'
        verbose_name = 'Товар в заказе'
        verbose_name_plural = 'Товары в заказе'

    def __str__(self):
        return f'{self.product.name} (x{self.quantity})'
