# Generated by Django 4.1.4 on 2023-01-23 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0014_alter_mergedtrade_exchange_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mergedtrade',
            name='order_execution_time',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='mergedtrade',
            name='trade_date',
            field=models.CharField(max_length=100, null=True),
        ),
    ]