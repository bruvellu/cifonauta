# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0010_auto_20150125_1224'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Country name.', unique=True, max_length=64, verbose_name='name')),
                ('name_pt_br', models.CharField(help_text='Country name.', max_length=64, unique=True, null=True, verbose_name='name')),
                ('name_en', models.CharField(help_text='Country name.', max_length=64, unique=True, null=True, verbose_name='name')),
                ('slug', models.SlugField(help_text='Country name slug.', max_length=64, verbose_name='slug', blank=True)),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this country.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this country.', verbose_name='number of videos', editable=False)),
            ],
            options={
                'verbose_name': 'country',
                'verbose_name_plural': 'country',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='state',
            options={'ordering': ['name'], 'verbose_name': 'state', 'verbose_name_plural': 'states'},
        ),
        migrations.AddField(
            model_name='image',
            name='country',
            field=models.ForeignKey(blank=True, to='meta.Country', help_text='Country shown in the image (or country where it was collected).', null=True, verbose_name='country', on_delete=models.DO_NOTHING),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='video',
            name='country',
            field=models.ForeignKey(blank=True, to='meta.Country', help_text='Country shown in the image (or country where it was collected).', null=True, verbose_name='country', on_delete=models.DO_NOTHING),
            preserve_default=True,
        ),
    ]
