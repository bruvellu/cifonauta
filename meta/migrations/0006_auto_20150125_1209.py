# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0005_auto_20150125_1205'),
    ]

    operations = [
        migrations.DeleteModel(
            name='City',
        ),
        migrations.AlterModelOptions(
            name='sublocation',
            options={'ordering': ['name'], 'verbose_name': 'city', 'verbose_name_plural': 'cities'},
        ),
    ]
