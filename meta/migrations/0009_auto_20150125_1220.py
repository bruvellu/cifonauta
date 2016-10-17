# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0008_auto_20150125_1219'),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='State name.', unique=True, max_length=64, verbose_name='name')),
                ('name_pt_br', models.CharField(help_text='State name.', max_length=64, unique=True, null=True, verbose_name='name')),
                ('name_en', models.CharField(help_text='State name.', max_length=64, unique=True, null=True, verbose_name='name')),
                ('slug', models.SlugField(help_text='State name slug.', max_length=64, verbose_name='slug', blank=True)),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this state.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this state.', verbose_name='number of videos', editable=False)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'state',
                'verbose_name_plural': 'states',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='city',
            options={'ordering': ['name'], 'verbose_name': 'city', 'verbose_name_plural': 'cities'},
        ),
        migrations.AddField(
            model_name='image',
            name='state',
            field=models.ForeignKey(blank=True, to='meta.State', help_text='State shown in the image (or state where it was collected).', null=True, verbose_name='state'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='video',
            name='state',
            field=models.ForeignKey(blank=True, to='meta.State', help_text='State shown in the image (or state where it was collected).', null=True, verbose_name='state'),
            preserve_default=True,
        ),
    ]
