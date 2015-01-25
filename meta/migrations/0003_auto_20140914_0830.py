# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0002_auto_20140914_0813'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='name_en',
            field=models.CharField(help_text='City name.', max_length=64, unique=True, null=True, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='city',
            name='name_pt_br',
            field=models.CharField(help_text='City name.', max_length=64, unique=True, null=True, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='country',
            name='name_en',
            field=models.CharField(help_text='Country name.', max_length=64, unique=True, null=True, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='country',
            name='name_pt_br',
            field=models.CharField(help_text='Country name.', max_length=64, unique=True, null=True, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='caption_en',
            field=models.TextField(help_text='Image caption.', null=True, verbose_name='caption', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='caption_pt_br',
            field=models.TextField(help_text='Image caption.', null=True, verbose_name='caption', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='title_en',
            field=models.CharField(help_text='Image title.', max_length=200, null=True, verbose_name='title', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='title_pt_br',
            field=models.CharField(help_text='Image title.', max_length=200, null=True, verbose_name='title', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='state',
            name='name_en',
            field=models.CharField(help_text='State name.', max_length=64, unique=True, null=True, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='state',
            name='name_pt_br',
            field=models.CharField(help_text='State name.', max_length=64, unique=True, null=True, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tag',
            name='description_en',
            field=models.TextField(help_text='Tag description.', null=True, verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tag',
            name='description_pt_br',
            field=models.TextField(help_text='Tag description.', null=True, verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tag',
            name='name_en',
            field=models.CharField(help_text='Tag name.', max_length=64, unique=True, null=True, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tag',
            name='name_pt_br',
            field=models.CharField(help_text='Tag name.', max_length=64, unique=True, null=True, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tagcategory',
            name='description_en',
            field=models.TextField(help_text='Tag category description.', null=True, verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tagcategory',
            name='description_pt_br',
            field=models.TextField(help_text='Tag category description.', null=True, verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tagcategory',
            name='name_en',
            field=models.CharField(help_text='Tag category name.', max_length=64, unique=True, null=True, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tagcategory',
            name='name_pt_br',
            field=models.CharField(help_text='Tag category name.', max_length=64, unique=True, null=True, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='taxon',
            name='common_en',
            field=models.CharField(help_text='Taxon common name.', max_length=256, null=True, verbose_name='common name', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='taxon',
            name='common_pt_br',
            field=models.CharField(help_text='Taxon common name.', max_length=256, null=True, verbose_name='common name', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='taxon',
            name='rank_en',
            field=models.CharField(help_text='Taxonomic rank of a taxon.', max_length=256, null=True, verbose_name='rank', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='taxon',
            name='rank_pt_br',
            field=models.CharField(help_text='Taxonomic rank of a taxon.', max_length=256, null=True, verbose_name='rank', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tour',
            name='description_en',
            field=models.TextField(help_text='Tour description.', null=True, verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tour',
            name='description_pt_br',
            field=models.TextField(help_text='Tour description.', null=True, verbose_name='description', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tour',
            name='name_en',
            field=models.CharField(help_text='Tour name.', max_length=100, unique=True, null=True, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tour',
            name='name_pt_br',
            field=models.CharField(help_text='Tour name.', max_length=100, unique=True, null=True, verbose_name='name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='video',
            name='caption_en',
            field=models.TextField(help_text='Image caption.', null=True, verbose_name='caption', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='video',
            name='caption_pt_br',
            field=models.TextField(help_text='Image caption.', null=True, verbose_name='caption', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='video',
            name='title_en',
            field=models.CharField(help_text='Image title.', max_length=200, null=True, verbose_name='title', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='video',
            name='title_pt_br',
            field=models.CharField(help_text='Image title.', max_length=200, null=True, verbose_name='title', blank=True),
            preserve_default=True,
        ),
    ]
