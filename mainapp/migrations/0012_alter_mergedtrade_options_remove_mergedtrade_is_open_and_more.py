# Generated by Django 4.1.4 on 2023-01-23 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0011_alter_importtrade_file'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='mergedtrade',
            options={'ordering': ('order_execution_time',)},
        ),
        migrations.RemoveField(
            model_name='mergedtrade',
            name='is_open',
        ),
        migrations.RemoveField(
            model_name='mergedtrade',
            name='isin',
        ),
        migrations.RemoveField(
            model_name='mergedtrade',
            name='order_exec_time',
        ),
        migrations.RemoveField(
            model_name='mergedtrade',
            name='trade_id',
        ),
        migrations.AddField(
            model_name='brocker',
            name='options_rule',
            field=models.TextField(default="{\n    'calls': [None, ''],\n    'puts': [None, ''],\n}\n"),
        ),
        migrations.AddField(
            model_name='mergedtrade',
            name='assets_type',
            field=models.CharField(choices=[('cash', 'Cash'), ('equity_options', 'Equity Options'), ('equity_futures', 'Equity Futures'), ('forex_spot', 'Forex Spot'), ('forex_futures', 'Forex Futures'), ('forex_options', 'Forex Options'), ('commodity_futures', 'Commodity Futures'), ('commodity_options', 'Commodity Options'), ('crypto_spot', 'Crypto Spot'), ('crypto_futures', 'Crypto Futures'), ('crypto_options', 'Crypto\xa0Options')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='mergedtrade',
            name='expiry_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='mergedtrade',
            name='options_type',
            field=models.CharField(choices=[('calls', 'Calls'), ('puts', 'Puts')], max_length=5, null=True),
        ),
        migrations.AddField(
            model_name='mergedtrade',
            name='order_execution_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='mergedtrade',
            name='strike_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='brocker',
            name='assets_rule',
            field=models.TextField(default="{\n    'cash': [None, ''],\n    'equity_options': [[None, ''], [None, '']],\n    'equity_futures': [[None, ''], [None, '']],\n    'forex_spot':  [None, ''],\n    'forex_options': [[None, ''], [None, '']],\n    'forex_futures': [[None, ''], [None, '']],\n    'commodity_futures': [[None, ''], [None, '']],\n    'commodity_options': [[None, ''], [None, '']],\n    'crypto_spot': [None, ''],\n    'crypto_futures':  [None, ''],\n    'crypto_options':  [None, ''],\n}\n"),
        ),
        migrations.AlterField(
            model_name='brocker',
            name='fields_rule',
            field=models.TextField(default="{\n    'symbol': [None, ''],\n    'trade_date': [None, ''],\n    'exchange': [None, ''],\n    'segment': [None, ''],\n    'trade_type': [None, ''],\n    'quantity': [None, ''],\n    'price': [None, ''],\n    'order_id': [None, ''],\n    'order_execution_time': [None, ''],\n    'strike_price': [None, ''],\n    'expiry_date': [None, ''],\n    'options_type': [0, r'.*'],\n}"),
        ),
        migrations.AlterField(
            model_name='mergedtrade',
            name='trade_date',
            field=models.DateField(null=True),
        ),
    ]