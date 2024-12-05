# Generated by Django 5.1.2 on 2024-12-05 08:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_remove_product_characteristics_alter_product_price_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Series',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Название серии')),
            ],
            options={
                'verbose_name': 'Серия',
                'verbose_name_plural': 'Серии',
                'db_table': 'series',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='series',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='api.series', verbose_name='Серия'),
        ),
    ]
