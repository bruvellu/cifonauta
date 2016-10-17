# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0013_auto_20150125_1854'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Tag name.', unique=True, max_length=64, verbose_name='name')),
                ('name_pt_br', models.CharField(help_text='Tag name.', max_length=64, unique=True, null=True, verbose_name='name')),
                ('name_en', models.CharField(help_text='Tag name.', max_length=64, unique=True, null=True, verbose_name='name')),
                ('slug', models.SlugField(help_text='Tag name slug.', max_length=64, verbose_name='slug', blank=True)),
                ('description', models.TextField(help_text='Tag description.', verbose_name='description', blank=True)),
                ('description_pt_br', models.TextField(help_text='Tag description.', null=True, verbose_name='description', blank=True)),
                ('description_en', models.TextField(help_text='Tag description.', null=True, verbose_name='description', blank=True)),
                ('position', models.PositiveIntegerField(default=0, help_text='Define tag order in a queryset.', verbose_name='position')),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this tag.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this tag.', verbose_name='number of videos', editable=False)),
                ('images', models.ManyToManyField(help_text='Photos linked to this tag.', to='meta.Image', null=True, verbose_name='photos', blank=True)),
                ('parent', models.ForeignKey(related_name=b'tags', blank=True, to='meta.TagCategory', help_text='Category to which this tag belongs.', null=True, verbose_name='father')),
                ('videos', models.ManyToManyField(help_text='Videos linked to this tag.', to='meta.Video', null=True, verbose_name='videos', blank=True)),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='source',
            options={'ordering': ['name'], 'verbose_name': 'expert', 'verbose_name_plural': 'experts'},
        ),
    ]
