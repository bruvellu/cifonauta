# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0009_auto_20150125_1220'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='state',
            options={'verbose_name': 'country', 'verbose_name_plural': 'country'},
        ),
        migrations.RemoveField(
            model_name='image',
            name='country',
        ),
        migrations.RemoveField(
            model_name='video',
            name='country',
        ),
        migrations.DeleteModel(
            name='Country',
        ),
    ]
