from django.contrib import admin
from django.forms import TextInput
from django.urls import reverse
from django.utils.safestring import mark_safe

from api.models import *
from concreteDecor.admin import admin_site


class EditLinkToInlineObject(object):
    def edit_link(self, instance):
        if instance.pk:
            url = reverse('admin:%s_%s_change' % (instance._meta.app_label, instance._meta.model_name),
                          args=[instance.pk])
            return mark_safe(
                u'<a class="related-widget-wrapper-link change-related" id="change" data-popup="yes" title="Change selected" href="{u}?_to_field=id&amp;_popup=1"><img src="/static/admin/img/icon-changelink.svg" alt="" width="20" height="20"></a>'.format(
                    u=url))
        else:
            url = reverse('admin:%s_%s_add' % (instance._meta.app_label, instance._meta.model_name))
            return mark_safe(
                u'<a class="related-widget-wrapper-link add-related" id="add" data-popup="yes" href="{u}?_to_field=id&amp;_popup=1" title="Add another"><img src="/static/admin/img/icon-addlink.svg" alt="" width="20" height="20"></a>'.format(
                    u=url))


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Показывать одну пустую форму для добавления изображения
    classes = ['collapse', ]


class ProductCharacteristicInline(admin.StackedInline):
    model = ProductCharacteristic
    extra = 1  # Показывает одну пустую форму для добавления новой характеристики
    verbose_name = "Характеристика"
    verbose_name_plural = "Характеристики"
    classes = ['collapse', ]


class ExpenseItemInline(admin.TabularInline):
    """ Inline для категорий расходов """
    model = ExpenseItem
    extra = 0
    verbose_name = "Расход"
    verbose_name_plural = "Расходы"


class ProductPriceHistoryAdmin(admin.ModelAdmin):
    """ Отображение истории цен товара """
    model = ProductPriceHistory
    inlines = [ExpenseItemInline]


class ProductPriceHistoryInline(EditLinkToInlineObject, admin.TabularInline):
    """ Отображение истории цен товара """
    model = ProductPriceHistory
    extra = 0  # Убирает «пустые» дополнительные строки
    fields = ('date', 'price', 'all_expenses', 'total_expenses', 'difference', 'edit_link')
    readonly_fields = ('edit_link', 'all_expenses', 'total_expenses', 'difference',)
    classes = ['collapse', ]
    show_change_link = True

    def all_expenses(self, obj):
        return obj.formatted_expenses

    all_expenses.short_description = "Расходы (категория + сумма)"

    def total_expenses(self, obj):
        return obj.total_expenses

    total_expenses.short_description = "Общая сумма расходов"

    def difference(self, obj):
        """Вычисляемое поле: цена - расходы."""
        return obj.price - obj.total_expenses if obj.price else '-'

    difference.short_description = "Прибыль"


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductCharacteristicInline, ProductImageInline, ProductPriceHistoryInline]
    list_display = ('name', 'price', 'stock')  # Поля, которые будут отображаться в списке товаров
    list_filter = ('series',)
    search_fields = ('name', 'description')  # Поиск по названию и описанию

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Переопределяем поле color, чтобы отображать его как color picker.
        """
        if db_field.name == 'color':
            kwargs['widget'] = TextInput(attrs={'type': 'color'})
        return super().formfield_for_dbfield(db_field, request, **kwargs)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Количество пустых строк для добавления новых товаров
    fields = ('product', 'quantity', 'price')
    readonly_fields = ('price',)  # Цена обычно фиксируется при оформлении заказа


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at', 'updated_at')
    list_editable = ('status',)
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'id')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'shipping_address', 'delivery_method', 'delivery_cost', 'promo_code')
        }),
        ('Статус и стоимость', {
            'fields': ('status', 'total_price', 'created_at', 'updated_at')
        }),
    )

    inlines = [OrderItemInline]


admin_site.register(Category)
admin_site.register(Cart)
admin_site.register(CartItem)
admin_site.register(PromoCode)
admin_site.register(PromoCodeUsage)
admin_site.register(CustomUser)
admin_site.register(Order, OrderAdmin)
admin_site.register(OrderItem)
admin_site.register(Series)
admin_site.register(ProductPriceHistory, ProductPriceHistoryAdmin)
admin_site.register(Product, ProductAdmin)
