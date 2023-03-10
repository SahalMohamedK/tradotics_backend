# Generated by Django 4.1.4 on 2023-03-07 19:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0035_tradehistory_portfolio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='portfolio',
            name='value',
        ),
        migrations.CreateModel(
            name='PortfolioEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(0, 'Deposit')], default=0)),
                ('value', models.DecimalField(decimal_places=2, max_digits=10)),
                ('date', models.DateTimeField()),
                ('desc', models.TextField()),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainapp.portfolio')),
            ],
        ),
    ]