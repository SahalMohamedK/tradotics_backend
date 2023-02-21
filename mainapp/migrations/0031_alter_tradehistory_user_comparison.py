# Generated by Django 4.1.4 on 2023-02-21 00:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainapp', '0030_tradehistory_is_demo_alter_tradehistory_brocker'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tradehistory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Comparison',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filters1', models.JSONField()),
                ('filters2', models.JSONField()),
                ('name', models.CharField(max_length=225)),
                ('desc', models.CharField(max_length=350)),
                ('group1', models.SmallIntegerField(choices=[(0, 'View'), (1, 'Edit')])),
                ('group2', models.SmallIntegerField(choices=[(0, 'View'), (1, 'Edit')])),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
