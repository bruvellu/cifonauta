# Generated by Django 4.2.1 on 2023-12-12 03:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0198_modifiedmedia2'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modifiedmedia2',
            options={'verbose_name': 'Modified Media 2', 'verbose_name_plural': 'Modified Media 2'},
        ),
        migrations.DeleteModel(
            name='ModifiedMedia',
        ),
    ]
