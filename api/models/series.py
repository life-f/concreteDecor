from django.db import models


class Series(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название серии")

    class Meta:
        db_table = "series"
        verbose_name = "Серия"
        verbose_name_plural = "Серии"

    def __str__(self):
        return self.name
