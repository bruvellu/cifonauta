# Generated by Django 2.2.5 on 2019-09-19 21:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0047_auto_20190915_1023'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='city',
        ),
        migrations.RemoveField(
            model_name='image',
            name='country',
        ),
        migrations.RemoveField(
            model_name='image',
            name='size',
        ),
        migrations.RemoveField(
            model_name='image',
            name='state',
        ),
        migrations.RemoveField(
            model_name='image',
            name='sublocation',
        ),
        migrations.RemoveField(
            model_name='source',
            name='images',
        ),
        migrations.RemoveField(
            model_name='source',
            name='videos',
        ),
        migrations.RemoveField(
            model_name='video',
            name='city',
        ),
        migrations.RemoveField(
            model_name='video',
            name='country',
        ),
        migrations.RemoveField(
            model_name='video',
            name='size',
        ),
        migrations.RemoveField(
            model_name='video',
            name='state',
        ),
        migrations.RemoveField(
            model_name='video',
            name='sublocation',
        ),
        migrations.RemoveField(
            model_name='reference',
            name='images',
        ),
        migrations.RemoveField(
            model_name='reference',
            name='videos',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='images',
        ),
        migrations.RemoveField(
            model_name='tag',
            name='videos',
        ),
        migrations.RemoveField(
            model_name='taxon',
            name='images',
        ),
        migrations.RemoveField(
            model_name='taxon',
            name='videos',
        ),
        migrations.RemoveField(
            model_name='tour',
            name='images',
        ),
        migrations.RemoveField(
            model_name='tour',
            name='videos',
        ),
        migrations.DeleteModel(
            name='Author',
        ),
        migrations.DeleteModel(
            name='Image',
        ),
        migrations.DeleteModel(
            name='Source',
        ),
        migrations.DeleteModel(
            name='Video',
        ),
    ]
