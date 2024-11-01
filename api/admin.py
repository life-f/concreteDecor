from django.contrib import admin

from api.models import *

# admin.site.register(Product)
# admin.site.register(ProductImage)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(PromoCode)
admin.site.register(PromoCodeUsage)
admin.site.register(CustomUser)
admin.site.register(Order)
admin.site.register(OrderItem)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Показывать одну пустую форму для добавления изображения


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name', 'price', 'stock')  # Поля, которые будут отображаться в списке товаров


admin.site.register(Product, ProductAdmin)
