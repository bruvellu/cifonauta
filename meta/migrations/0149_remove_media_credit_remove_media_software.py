# Generated by Django 4.2.3 on 2023-11-01 21:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0148_remove_media_habitat_remove_media_life_stage_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='credit',
        ),
        migrations.RemoveField(
            model_name='media',
            name='software',
        ),
    ]
