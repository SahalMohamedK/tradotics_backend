# Generated by Django 4.1.4 on 2023-01-23 15:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_rename_phone_profile_phonenumber'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='phoneNumber',
            new_name='phone_number',
        ),
    ]
