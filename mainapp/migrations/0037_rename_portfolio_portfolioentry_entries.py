# Generated by Django 4.1.4 on 2023-03-07 20:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0036_remove_portfolio_value_portfolioentry'),
    ]

    operations = [
        migrations.RenameField(
            model_name='portfolioentry',
            old_name='portfolio',
            new_name='entries',
        ),
    ]