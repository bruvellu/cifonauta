# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0011_auto_20150125_1226'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='filepath',
            field=models.CharField(help_text='Local source file.', max_length=200, null=True, verbose_name='arquivo fonte local (novo)', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='video',
            name='filepath',
            field=models.CharField(help_text='Local source file.', max_length=200, null=True, verbose_name='arquivo fonte local (novo)', blank=True),
            preserve_default=True,
        ),
    ]
