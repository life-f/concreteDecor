from django.db import models
from decimal import Decimal
from django.contrib.auth import get_user_model

from api.models import CustomUser
from api.models.order import Order

User = get_user_model()


class UnitEconomicsRecord(models.Model):
    """
    Модель для хранения внешних данных для расчёта юнит‑экономики.
    Поля visitors, cost_per_visitor вводятся вручную.

    Поля registered_users и buyers вычисляются динамически
    """
    date = models.DateField(verbose_name="Дата", unique=True)
    visitors = models.PositiveIntegerField(verbose_name="Посетители (v)", default=0)
    cost_per_visitor = models.DecimalField(verbose_name="Стоимость одного посетителя", max_digits=10, decimal_places=2,
                                           default=Decimal('0.00'))

    class Meta:
        db_table = 'unit_economics_record'
        verbose_name = "Внешние данные (юнит)"
        verbose_name_plural = "Внешние данные (юнит)"
        ordering = ['-date']

    def __str__(self):
        return f"UE {self.date}"

    # --- Вычисляемые показатели ---

    @property
    def marketing_cost(self):
        """Расходы на посетителей: visitors * cost_per_visitor"""
        return self.visitors * self.cost_per_visitor

    @property
    def gross_profit(self):
        """Валовая прибыль: маржа - себестоимость"""
        return 0 #self.margin_from_sales - self.cogs

    @property
    def profit_after_marketing(self):
        """Прибыль после маркетинга: валовая прибыль - расходы на посетителей"""
        return self.gross_profit - self.marketing_cost

    @property
    def registered_users(self):
        """
        Количество зарегистрированных пользователей
        """
        return CustomUser.objects.filter(date_joined__date__lte=self.date).count()

    @property
    def buyers(self):
        """
        Количество покупателей
        Покупателями считаются те, у кого имеется хотя бы один заказ,
        при этом считается только первый заказ для каждого пользователя.
        """
        new_users = CustomUser.objects.filter(date_joined__date__lte=self.date)
        count = 0
        for user in new_users:
            first_order = Order.objects.filter(user=user).order_by('created_at').first()
            if first_order:
                count += 1
        return count
