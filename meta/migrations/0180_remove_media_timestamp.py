# Generated by Django 4.2.7 on 2023-11-19 14:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0179_alter_media_date_modified_alter_media_date_uploaded'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='timestamp',
        ),
    ]
