# Generated by Django 4.2.11 on 2024-07-06 12:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0226_auto_20240613_2011'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='city',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='city',
            name='name_pt_br',
        ),
        migrations.RemoveField(
            model_name='state',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='state',
            name='name_pt_br',
        ),
    ]
