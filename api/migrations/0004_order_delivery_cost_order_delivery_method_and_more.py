# Generated by Django 5.1.2 on 2024-11-01 11:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='delivery_cost',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Стоимость доставки'),
        ),
        migrations.AddField(
            model_name='order',
            name='delivery_method',
            field=models.CharField(default='Самовывоз', max_length=20, verbose_name='Способ доставки'),
        ),
        migrations.AddField(
            model_name='order',
            name='promo_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.promocode', verbose_name='Промокод'),
        ),
    ]
