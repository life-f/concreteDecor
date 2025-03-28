from django.contrib import admin
from django.forms import TextInput

from api.models import *
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token

import matplotlib.pyplot as plt
import io
import urllib
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.db.models.functions import TruncDate
from django.db.models import Count
from datetime import datetime, timedelta
from django.http import HttpResponse


class AnalyticsAdminSite(admin.AdminSite):
    """
    Кастомная панель администратора с аналитикой заказов и клиентов.
    """
    site_header = "Административная панель"
    site_title = "Админ-панель"
    index_title = "Добро пожаловать в админ-панель"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("analytics/", self.admin_view(self.analytics_view), name="analytics"),
            path("analytics/chart/orders", self.admin_view(self.analytics_chart_orders), name="analytics_chart_orders"),
            path("analytics/chart/clients", self.admin_view(self.analytics_chart_clients), name="analytics_chart_clients"),
        ]
        return custom_urls + urls

    def analytics_view(self, request):
        """
        Страница аналитики с графиком.
        """
        return render(request, "admin/global_stat.html", {})

    def analytics_chart_orders(self, request):
        """
        Генерация и отправка графика заказов как изображения.
        """
        period = request.GET.get("period", "month")

        if period == "week":
            start_date = datetime.now() - timedelta(days=7)
        elif period == "month":
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = datetime.now() - timedelta(days=int(period))

        # Группировка заказов по дням
        orders_per_day = (
            Order.objects.filter(created_at__gte=start_date)
            .annotate(date=TruncDate("created_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        dates = [entry["date"] for entry in orders_per_day]
        order_counts = [entry["count"] for entry in orders_per_day]

        # Создаём график
        fig, ax = plt.subplots()
        ax.plot(dates, order_counts, marker="o", linestyle="-", label="Заказы", color="blue")

        ax.set_title("Статистика заказов")
        ax.set_xlabel("Дата")
        ax.set_ylabel("Количество")
        ax.legend()
        ax.grid(True)

        # Конвертируем график в изображение
        buffer = io.BytesIO()
        plt.xticks(rotation=45)
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        return HttpResponse(buffer.getvalue(), content_type="image/png")

    def analytics_chart_clients(self, request):
        """
        Генерация и отправка графика клиентов как изображения.
        """
        period = request.GET.get("period", "month")

        if period == "week":
            start_date = datetime.now() - timedelta(days=7)
        elif period == "month":
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = datetime.now() - timedelta(days=int(period))

        # Группировка новых клиентов по дням
        clients_per_day = (
            CustomUser.objects.filter(date_joined__gte=start_date)
            .annotate(date=TruncDate("date_joined"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        client_dates = [entry["date"] for entry in clients_per_day]
        client_counts = [entry["count"] for entry in clients_per_day]

        # Создаём график
        fig, ax = plt.subplots()
        ax.plot(client_dates, client_counts, marker="o", linestyle="-", label="Новые клиенты", color="green")

        ax.set_title("Статистика клиентов")
        ax.set_xlabel("Дата")
        ax.set_ylabel("Количество")
        ax.legend()
        ax.grid(True)

        # Конвертируем график в изображение
        buffer = io.BytesIO()
        plt.xticks(rotation=45)
        plt.savefig(buffer, format="png")
        buffer.seek(0)

        return HttpResponse(buffer.getvalue(), content_type="image/png")

    def get_app_list(self, request, app_label=None):
        """
        Добавляет "Аналитику" в список доступных разделов админки.
        """
        app_list = super().get_app_list(request, app_label)
        analytics_entry = {
            "name": "Аналитика",
            "app_label": "analytics",
            "app_url": reverse("admin:analytics"),
            "models": [],
        }
        app_list.insert(1, analytics_entry)
        return app_list


admin_site = AnalyticsAdminSite(name="admin")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Показывать одну пустую форму для добавления изображения


class ProductCharacteristicInline(admin.StackedInline):
    model = ProductCharacteristic
    extra = 1  # Показывает одну пустую форму для добавления новой характеристики
    verbose_name = "Характеристика"
    verbose_name_plural = "Характеристики"


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductCharacteristicInline, ProductImageInline]
    list_display = ('name', 'price', 'stock')  # Поля, которые будут отображаться в списке товаров
    list_filter = ('series',)
    search_fields = ('name', 'description')  # Поиск по названию и описанию
    fields = ('name', 'description', 'price', 'stock', 'series', 'color', 'category')  # Поля для редактирования

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Переопределяем поле color, чтобы отображать его как color picker.
        """
        if db_field.name == 'color':
            kwargs['widget'] = TextInput(attrs={'type': 'color'})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(PromoCode)
admin.site.register(PromoCodeUsage)
admin.site.register(CustomUser)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Series)
admin.site.register(Product, ProductAdmin)

admin_site.register(Category)
admin_site.register(Cart)
admin_site.register(CartItem)
admin_site.register(PromoCode)
admin_site.register(PromoCodeUsage)
admin_site.register(CustomUser)
admin_site.register(Order)
admin_site.register(OrderItem)
admin_site.register(Series)
admin_site.register(Product, ProductAdmin)
admin_site.register(Token)
admin_site.register(Group)
