from django.core.exceptions import ValidationError
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название товара')
    category = models.ManyToManyField('Category', verbose_name='Категория', related_name='products', blank=True)
    series = models.ForeignKey("Series", on_delete=models.PROTECT, null=True, blank=True, related_name="products",
                               verbose_name="Серия")
    color = models.CharField(max_length=7, verbose_name="Цвет товара (для серий)", null=True, blank=True)
    description = models.TextField(verbose_name='Описание товара')
    price = models.PositiveIntegerField(verbose_name='Цена')
    stock = models.PositiveIntegerField(verbose_name='Количество на складе')

    class Meta:
        db_table = 'product'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    def clean(self):
        """
        Валидируем цвет: оно должно быть задано только если серия указана.
        """
        if self.series and not self.color:
            raise ValidationError({'color': "Цвет обязателен, если указана серия."})
        if not self.series and self.color:
            raise ValidationError({'color': "Цвет нельзя указывать без серии."})
        # Валидируем формат цвета (HEX)
        if self.color and not self.color.startswith('#') or len(self.color) != 7:
            raise ValidationError({'color': "Цвет должен быть задан в формате HEX (#RRGGBB)."})

class ProductCharacteristic(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='characteristics', verbose_name='Товар')
    key = models.CharField(max_length=255, verbose_name='Название характеристики')
    value = models.CharField(max_length=255, verbose_name='Значение характеристики')

    class Meta:
        db_table = 'product_characteristic'
        verbose_name = 'Характеристика товара'
        verbose_name_plural = 'Характеристики товара'

    def __str__(self):
        return f"{self.key}: {self.value}"


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')
    image = models.ImageField(upload_to='products/', verbose_name='Изображение')

    class Meta:
        db_table = 'product_image'
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'

    def __str__(self):
        return f'Изображение для {self.product.name}'
