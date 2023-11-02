# Generated by Django 4.2.3 on 2023-10-29 14:19

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0131_media_search_vector'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='media',
            index=django.contrib.postgres.indexes.GinIndex(fields=['search_vector'], name='meta_media_search__fc903c_gin'),
        ),
    ]