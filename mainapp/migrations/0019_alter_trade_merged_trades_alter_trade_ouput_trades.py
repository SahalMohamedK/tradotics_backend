# Generated by Django 4.1.4 on 2023-01-24 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0018_trade_delete_mergedtrade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='merged_trades',
            field=models.FilePathField(),
        ),
        migrations.AlterField(
            model_name='trade',
            name='ouput_trades',
            field=models.FilePathField(),
        ),
    ]