# Generated by Django 4.2.3 on 2023-11-02 16:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0155_auto_20231102_1326'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='media',
        ),
    ]
