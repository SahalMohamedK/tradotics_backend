# Generated by Django 4.1.4 on 2023-01-24 08:29

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('mainapp', '0017_mergedtrade_delete_importtrade'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merged_trades', models.FileField(upload_to='merged_trades', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['csv'])])),
                ('ouput_trades', models.FileField(upload_to='ouput_trades', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['csv'])])),
                ('created', models.DateTimeField(auto_now=True)),
                ('brocker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.brocker')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='merged_trades', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='MergedTrade',
        ),
    ]
