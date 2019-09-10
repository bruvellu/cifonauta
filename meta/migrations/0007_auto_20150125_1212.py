# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0006_auto_20150125_1209'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='City name.', unique=True, max_length=64, verbose_name='name')),
                ('name_pt_br', models.CharField(help_text='City name.', max_length=64, unique=True, null=True, verbose_name='name')),
                ('name_en', models.CharField(help_text='City name.', max_length=64, unique=True, null=True, verbose_name='name')),
                ('slug', models.SlugField(help_text='City name slug.', max_length=64, verbose_name='slug', blank=True)),
                ('image_count', models.PositiveIntegerField(default=0, help_text='Number of photos linked to this city.', verbose_name='number of photos', editable=False)),
                ('video_count', models.PositiveIntegerField(default=0, help_text='Number of videos linked to this city.', verbose_name='number of videos', editable=False)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'city',
                'verbose_name_plural': 'cities',
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='sublocation',
            options={'ordering': ['name'], 'verbose_name': 'place', 'verbose_name_plural': 'places'},
        ),
        migrations.AddField(
            model_name='image',
            name='city',
            field=models.ForeignKey(blank=True, to='meta.City', help_text='City shown in the image (or city where it was collected).', null=True, verbose_name=b'cidade', on_delete=models.DO_NOTHING),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='video',
            name='city',
            field=models.ForeignKey(blank=True, to='meta.City', help_text='City shown in the image (or city where it was collected).', null=True, verbose_name=b'cidade', on_delete=models.DO_NOTHING),
            preserve_default=True,
        ),
    ]
