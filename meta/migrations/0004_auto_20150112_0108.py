# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0003_auto_20140914_0830'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='filename',
            field=models.CharField(default='', help_text='Nome \xfanico e identificador do arquivo.', max_length=200, verbose_name='Nome \xfanico do arquivo.', blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='video',
            name='filename',
            field=models.CharField(default='empty string', help_text='Nome \xfanico e identificador do arquivo.', max_length=200, verbose_name='Nome \xfanico do arquivo.', blank=True),
            preserve_default=False,
        ),
    ]
