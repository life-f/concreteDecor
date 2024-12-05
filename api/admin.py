from django.contrib import admin

from api.models import *

admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(PromoCode)
admin.site.register(PromoCodeUsage)
admin.site.register(CustomUser)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Series)


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
    fields = ('name', 'description', 'price', 'stock', 'series', 'category')  # Поля для редактирования


admin.site.register(Product, ProductAdmin)
