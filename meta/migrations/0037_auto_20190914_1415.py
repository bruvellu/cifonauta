# Generated by Django 2.2.5 on 2019-09-14 14:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0036_auto_20190914_1412'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='taxon',
            name='common',
        ),
        migrations.RemoveField(
            model_name='taxon',
            name='common_en',
        ),
        migrations.RemoveField(
            model_name='taxon',
            name='common_pt_br',
        ),
    ]
