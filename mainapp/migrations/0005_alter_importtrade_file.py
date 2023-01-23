# Generated by Django 4.1.4 on 2023-01-21 20:53

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0004_alter_importtrade_brocker'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importtrade',
            name='file',
            field=models.FileField(upload_to='trade_uploads', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
    ]
