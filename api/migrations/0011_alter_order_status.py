# Generated by Django 5.1.2 on 2025-06-26 09:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_alter_expenseitem_options_alter_expenseitem_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('awaiting_pay', 'Ожидает оплаты'), ('pending', 'В ожидании'), ('confirmed', 'Подтвержден'), ('shipped', 'Отправлен'), ('delivered', 'Доставлен'), ('finished', 'Завершен'), ('canceled', 'Отменен')], default='awaiting_pay', max_length=20, verbose_name='Статус заказа'),
        ),
    ]
