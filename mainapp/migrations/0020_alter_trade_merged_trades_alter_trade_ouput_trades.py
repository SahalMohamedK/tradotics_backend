# Generated by Django 4.1.4 on 2023-01-24 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0019_alter_trade_merged_trades_alter_trade_ouput_trades'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trade',
            name='merged_trades',
            field=models.FilePathField(path='D:\\Users\\saifk\\Documents\\Sahal\\Ink Signature Designs\\artists\\ATT00001 Sahal Mohamed\\works\\Tradotics\\website\\backend\\media/merged_trades'),
        ),
        migrations.AlterField(
            model_name='trade',
            name='ouput_trades',
            field=models.FilePathField(path='D:\\Users\\saifk\\Documents\\Sahal\\Ink Signature Designs\\artists\\ATT00001 Sahal Mohamed\\works\\Tradotics\\website\\backend\\media/output_trades'),
        ),
    ]
