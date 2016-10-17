# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0007_auto_20150125_1212'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='city',
            options={'ordering': ['name'], 'verbose_name': 'state', 'verbose_name_plural': 'states'},
        ),
        migrations.RemoveField(
            model_name='image',
            name='state',
        ),
        migrations.RemoveField(
            model_name='video',
            name='state',
        ),
        migrations.DeleteModel(
            name='State',
        ),
    ]
