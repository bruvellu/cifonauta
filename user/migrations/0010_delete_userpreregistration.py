# Generated by Django 4.2.1 on 2023-08-10 18:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_userpreregistration_alter_usercifonauta_curator_of_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserPreRegistration',
        ),
    ]
