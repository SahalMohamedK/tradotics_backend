# Generated by Django 4.1.4 on 2023-01-21 20:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_importtrade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importtrade',
            name='brocker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.brocker'),
        ),
    ]
