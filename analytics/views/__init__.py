# analytics/views.py

from django import forms
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from api.models.user import CustomUser
from api.models.order import Order


class CohortAnalysisForm(forms.Form):
    start_date = forms.DateField(label="Начальная дата", required=False)
    end_date = forms.DateField(label="Конечная дата", required=False)
    cohort_size = forms.ChoiceField(
        label="Размер когорты",
        choices=[('7', 'Неделя (7 дней)'), ('30', 'Месяц (30 дней)'), ('custom', 'Произвольное')],
        initial='7'
    )
    custom_cohort_size = forms.IntegerField(label="Размер когорты (в днях)", required=False, min_value=1)


def cohort_analysis_view(request):
    today = timezone.now().date()
    default_start = today - timedelta(days=30)
    default_end = today
    initial_data = {
        'start_date': default_start,
        'end_date': default_end,
        'cohort_size': '7',
        'custom_cohort_size': 7,
    }
    form = CohortAnalysisForm(request.GET or None, initial=initial_data)
    table = None
    buckets_range = []
    if form.is_valid():
        start_date = form.cleaned_data['start_date'] or default_start
        end_date = form.cleaned_data['end_date'] or default_end
        cohort_size_choice = form.cleaned_data['cohort_size']
        if cohort_size_choice == 'custom':
            cohort_size = form.cleaned_data['custom_cohort_size'] or 7
        else:
            cohort_size = int(cohort_size_choice)

        # Выбираем пользователей, зарегистрированных в указанный период
        users = CustomUser.objects.filter(date_joined__date__gte=start_date, date_joined__date__lte=end_date)
        # Группируем пользователей по когорте: вычисляем смещение от start_date и округляем вниз по размеру когорты
        cohorts = {}
        for user in users:
            reg_date = user.date_joined.date()
            offset = (reg_date - start_date).days
            cohort_offset = (offset // cohort_size) * cohort_size
            cohort_start = start_date + timedelta(days=cohort_offset)
            cohorts.setdefault(cohort_start, []).append(user.id)

        # Для удобства создадим словарь: user_id -> cohort_start
        user_to_cohort = {}
        for cohort_start, user_ids in cohorts.items():
            for uid in user_ids:
                user_to_cohort[uid] = cohort_start

        # Выбираем все заказы пользователей из выбранных когорт
        orders = Order.objects.filter(user__id__in=list(user_to_cohort.keys()))
        # Результаты: results[cohort_start][bucket] = сумма заказов
        results = {}
        for order in orders:
            order_date = order.created_at.date()
            cohort_start = user_to_cohort.get(order.user_id)
            if not cohort_start:
                continue
            # Определяем смещение от начала когорты
            bucket = (order_date - cohort_start).days // cohort_size
            if bucket < 0:
                continue
            results.setdefault(cohort_start, {})
            results[cohort_start][bucket] = results[cohort_start].get(bucket, 0) + float(order.total_price)

        # Определяем максимальное число периодов (bucket) среди всех когорт
        max_bucket = 0
        for cohort_data in results.values():
            if cohort_data:
                max_bucket = max(max_bucket, max(cohort_data.keys()))
        buckets_range = range(max_bucket + 1)

        # Строим таблицу: список строк с когортой и списком значений по периодам
        table = []
        for cohort_start in sorted(cohorts.keys()):
            row = {
                'cohort_start': cohort_start,
                'buckets': [results.get(cohort_start, {}).get(i, 0) for i in buckets_range]
            }
            table.append(row)

    context = {
        'form': form,
        'table': table,
        'buckets_range': buckets_range,
    }
    return render(request, "admin/cohort_analysis.html", context)
