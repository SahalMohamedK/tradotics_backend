# Generated by Django 4.1.4 on 2023-01-22 08:43

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainapp', '0005_alter_importtrade_file'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ImportTrade',
            new_name='ImportTrades',
        ),
    ]
