# Generated by Django 4.1.4 on 2023-01-24 13:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0022_alter_trade_merged_trades_alter_trade_ouput_trades'),
    ]

    operations = [
        migrations.RenameField(
            model_name='trade',
            old_name='ouput_trades',
            new_name='output_trades',
        ),
    ]
