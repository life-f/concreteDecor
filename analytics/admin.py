import io
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from django.contrib import admin
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path

from api.models import CustomUser, Cart, ExpenseItem
from api.models import Order
from concreteDecor.admin import admin_site
from .models import UnitEconomics, CohortAnalysis, Statistic, UnitEconomicsRecord


class ClientOrdersPageAdmin(admin.ModelAdmin):
    """
    Админ-класс для «Аналитики продаж и клиентов».
    """

    # Отключаем добавление/удаление, чтобы не было лишних действий
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return

    def get_urls(self):
        # Получаем стандартные URL'ы для этой модели
        urls = super().get_urls()
        # Добавляем свои URL'ы
        custom_urls = [
            path("analytics/chart/orders", self.admin_site.admin_view(self.analytics_chart_orders),
                 name="analytics_chart_orders"),
            path("analytics/chart/clients", self.admin_site.admin_view(self.analytics_chart_clients),
                 name="analytics_chart_clients"),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        context = {
            **(extra_context or {}),
            'title': "Аналитика заказов и клиентов",
            'opts': self.model._meta,
        }
        return TemplateResponse(request, "admin/global_stat.html", context)

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


class UnitEconomicsPageAdmin(admin.ModelAdmin):
    """
    Админ-класс для «Юнит-экономика».
    """

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        return self.unit_economics_view(request)

    def unit_economics_view(self, request):
        # если нет даты — берём последний месяц
        today = datetime.today()
        default_start = today - timedelta(days=30)
        start_date = datetime.strptime(request.GET.get("start_date"), "%Y-%m-%d").date() if request.GET.get(
            "start_date") else default_start
        end_date = datetime.strptime(request.GET.get("end_date"), "%Y-%m-%d").date() if request.GET.get(
            "end_date") else today

        # Подготовка к расчету маркетинга (CAC)
        last_ue_record = UnitEconomicsRecord.objects.all().order_by("-date").first()
        v = request.GET.get("v") if request.GET.get("v") else last_ue_record.visitors
        CPV = request.GET.get("CPV") if request.GET.get("CPV") else last_ue_record.cost_per_visitor
        users = CustomUser.objects.filter(date_joined__gte=start_date, date_joined__lte=end_date)
        u = users.count()
        orders = Order.objects.filter(user__in=users)
        p = orders.distinct(
            'user').count()  # количество первых заказов - количество новых покупателей, количество оформленных корзин
        carts = Cart.objects.filter(user__in=users)
        c = carts.distinct('user').count()  # количество неоформленных корзин
        cogs = (orders.filter(items__product__price_history__isnull=False)
                .annotate(total_expenses=Sum("items__product__price_history__expenses__cost"))).values_list(
            'total_expenses', flat=True)
        print(cogs)
        AVG_COGS = (float(sum(cogs)) / cogs.count()) if cogs.count() > 0 else 0  # средние затраты на товар

        # Расчет конверсий
        V2S_CR = (u / v) if v > 0 else 0
        V2C_CR = ((p + c) / v) if v > 0 else 0
        C2P_CR = (p / (p + c)) if (p + c) > 0 else 0
        S2P_CR = (p / u) if u > 0 else 0
        V2P_CR = (p / v) if v > 0 else 0
        CAC = (float(CPV) / V2P_CR) if V2P_CR > 0 else 0

        # Расчет средних показателей для этих пользователей
        AOV = (sum(orders.values_list('total_price',
                                      flat=True)) / orders.count()) if orders.count() > 0 else 0  # средний чек
        AOC = (orders.count() / u) if u > 0 else 0  # среднее количество заказов
        AIPC = (sum(orders.values_list('items__quantity',
                                       flat=True)) / orders.count()) if orders.count() > 0 else 0  # среднее количество товаров в корзине
        AIP = (sum(orders.values_list('total_price', flat=True)) / sum(
            orders.values_list('items__quantity', flat=True))) if sum(
            orders.values_list('items__quantity', flat=True)) > 0 else 0  # средняя цена товара в корзине
        ARPU = (sum(orders.values_list('total_price', flat=True)) / u) if u > 0 else 0  # средняя выручка с пользователя
        gross_per1 = float(ARPU) - float(CAC) - float(AVG_COGS)

        table = {
            "v": v,
            "CPV": CPV,
            "V2S_CR": V2S_CR,
            "V2C_CR": V2C_CR,
            "C2P_CR": C2P_CR,
            "S2P_CR": S2P_CR,
            "V2P_CR": V2P_CR,
            "CAC": CAC,
            "AOV": AOV,
            "AOC": AOC,
            "AIPC": AIPC,
            "AIP": AIP,
            "ARPU": ARPU,
            "gross_per1": gross_per1,
        }
        context = {
            "table": table,
            "start_date": start_date,
            "end_date": end_date,
            # "cohort_size": cohort_size,
            # "unit": unit,
            # 'units_select': units_select,
            'title': "Юнит-экономика",
            'opts': self.model._meta,
        }
        return TemplateResponse(request, "admin/unit_economics.html", context)


class CohortAnalysisPageAdmin(admin.ModelAdmin):
    """
    Админ-класс для «Когортный анализ».
    """

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_urls(self):
        # Получаем стандартные URL'ы для этой модели
        urls = super().get_urls()
        # Добавляем свои URL'ы
        custom_urls = [
            path("analytics/cohortanalysis/", self.admin_site.admin_view(self.cohort_analysis_view),
                 name='cohort-analysis'),

        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        return self.cohort_analysis_view(request)

    def cohort_analysis_view(self, request):
        # получаем параметры запроса
        start_str = request.GET.get("start_date")
        end_str = request.GET.get("end_date")
        cohort_size = int(request.GET.get("cohort_size", 7))

        # если нет даты — берём последний месяц
        today = datetime.today()
        default_start = today - timedelta(days=30)
        start_date = datetime.strptime(start_str, "%Y-%m-%d").date() if start_str else default_start
        end_date = datetime.strptime(end_str, "%Y-%m-%d").date() if end_str else today

        users = CustomUser.objects.filter(date_joined__date__range=(start_date, end_date))

        # Шаг 2. Рассчитываем когорты
        cohorts = []
        current = start_date
        while current <= end_date:
            cohort_start = current
            cohort_end = cohort_start + timedelta(days=cohort_size - 1)
            if cohort_end > end_date:
                cohort_end = end_date
            cohorts.append((cohort_start, cohort_end))
            current = cohort_end + timedelta(days=1)

        # Шаг 3. Определяем, какие пользователи в какую когорту попадают (по дате регистрации).
        # user_to_cohort_idx хранит номер когорты (индекс в списке cohorts)
        user_to_cohort_idx = {}
        for idx, (c_start, c_end) in enumerate(cohorts):
            # Берём пользователей, зарегистрировавшихся в [c_start, c_end]
            users_in_cohort = CustomUser.objects.filter(
                date_joined__date__gte=c_start,
                date_joined__date__lte=c_end
            ).values_list('id', flat=True)
            for uid in users_in_cohort:
                user_to_cohort_idx[uid] = idx
        # Шаг 4. Выбираем заказы всех этих пользователей
        orders = Order.objects.filter(user__in=user_to_cohort_idx.keys())

        # results[period][cohort] = сумма заказов
        from collections import defaultdict
        results = defaultdict(lambda: defaultdict(float))  # двухуровневый словарь

        for order in orders:
            cidx = user_to_cohort_idx[order.user_id]
            for c in range(len(cohorts)):
                if datetime.date(cohorts[c][0]) <= datetime.date(order.created_at) <= datetime.date(cohorts[c][1]):
                    results[c][cidx] += float(order.total_price)
        # Шаг 5. Строим структуру для шаблона
        # Каждая ячейка = results[period][cohort]
        table_rows = []
        for p in range(len(cohorts)):
            row = {
                'period': cohorts[p],
                'values': []
            }
            for cidx in range(len(cohorts)):
                if cohorts[p][0] < cohorts[cidx][0]:
                    row['values'].append('-')
                else:
                    val = results[p][cidx]
                    row['values'].append(val)
            table_rows.append(row)

        context = {
            "cohort_table": table_rows,
            "periods": cohorts,
            "start_date": start_date,
            "end_date": end_date,
            "cohort_size": cohort_size,
            "title": "Когортный анализ",
            "opts": self.model._meta,
        }

        return TemplateResponse(request, "admin/cohort_analysis.html", context)


admin_site.register(Statistic, ClientOrdersPageAdmin)
admin_site.register(UnitEconomics, UnitEconomicsPageAdmin)
admin_site.register(CohortAnalysis, CohortAnalysisPageAdmin)
admin_site.register(UnitEconomicsRecord)
