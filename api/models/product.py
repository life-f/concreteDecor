from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название товара')
    category = models.ManyToManyField('Category', verbose_name='Категория', related_name='products', blank=True)
    description = models.TextField(verbose_name='Описание товара')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    characteristics = models.JSONField(verbose_name="Характеристики", null=True, blank=True)
    stock = models.PositiveIntegerField(verbose_name='Количество на складе')

    class Meta:
        db_table = 'product'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')
    image = models.ImageField(upload_to='media/products/', verbose_name='Изображение')

    class Meta:
        db_table = 'product_image'
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'

    def __str__(self):
        return f'Изображение для {self.product.name}'
