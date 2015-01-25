# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0012_auto_20150125_1234'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='images',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='videos',
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
        migrations.AlterModelOptions(
            name='source',
            options={'verbose_name': 'tag', 'verbose_name_plural': 'tags'},
        ),
    ]
