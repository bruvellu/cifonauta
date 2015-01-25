# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0004_auto_20150112_0108'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='city',
        ),
        migrations.RemoveField(
            model_name='video',
            name='city',
        ),
    ]
