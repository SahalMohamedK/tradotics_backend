# Generated by Django 4.1.4 on 2023-01-24 09:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0020_alter_trade_merged_trades_alter_trade_ouput_trades'),
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
