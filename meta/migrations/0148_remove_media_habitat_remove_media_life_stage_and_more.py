# Generated by Django 4.2.3 on 2023-11-01 21:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0147_alter_media_city_alter_media_coverpath_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='habitat',
        ),
        migrations.RemoveField(
            model_name='media',
            name='life_stage',
        ),
        migrations.RemoveField(
            model_name='media',
            name='life_style',
        ),
        migrations.RemoveField(
            model_name='media',
            name='microscopy',
        ),
        migrations.RemoveField(
            model_name='media',
            name='photographic_technique',
        ),
        migrations.RemoveField(
            model_name='media',
            name='several',
        ),
    ]
