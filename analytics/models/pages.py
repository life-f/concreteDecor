from django.db import models


class Statistic(models.Model):
    """
    Фиктивная модель для раздела «Клиенты и заказы».
    """

    class Meta:
        managed = False
        verbose_name = "Клиенты и заказы"
        verbose_name_plural = "Клиенты и заказы"

    def __str__(self):
        return "Clients and orders (dummy)"


class UnitEconomics(models.Model):
    """
    Фиктивная модель для раздела «Юнит-экономика».
    """

    class Meta:
        managed = False
        verbose_name = "Юнит-экономика"
        verbose_name_plural = "Юнит-экономика"

    def __str__(self):
        return "Unit Economics (dummy)"


class CohortAnalysis(models.Model):
    """
    Фиктивная модель для раздела «Когортный анализ».
    """

    class Meta:
        managed = False
        verbose_name = "Когортный анализ"
        verbose_name_plural = "Когортный анализ"

    def __str__(self):
        return "Cohort Analysis (dummy)"
