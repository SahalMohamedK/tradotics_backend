# Generated by Django 4.1.4 on 2023-01-21 09:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_rename_phonenumber_profile_phone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='phone',
            new_name='phoneNumber',
        ),
    ]
