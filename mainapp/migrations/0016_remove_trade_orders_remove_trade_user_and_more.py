# Generated by Django 4.1.4 on 2023-01-23 22:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0015_alter_mergedtrade_order_execution_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trade',
            name='orders',
        ),
        migrations.RemoveField(
            model_name='trade',
            name='user',
        ),
        migrations.DeleteModel(
            name='MergedTrade',
        ),
        migrations.DeleteModel(
            name='Trade',
        ),
    ]