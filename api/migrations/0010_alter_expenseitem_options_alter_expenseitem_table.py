# Generated by Django 5.1.2 on 2025-04-03 13:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_productpricehistory_expenseitem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='expenseitem',
            options={'verbose_name': 'Категория расхода', 'verbose_name_plural': 'Категории расхода'},
        ),
        migrations.AlterModelTable(
            name='expenseitem',
            table='expence_item',
        ),
    ]
