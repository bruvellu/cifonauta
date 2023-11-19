# Generated by Django 4.2.7 on 2023-11-19 11:18

from django.db import migrations


def convert_old_dates_to_null(apps, schema_editor):
    '''Convert creation dates before 1950s to null.'''

    Media = apps.get_model('meta', 'Media')

    Media.objects.filter(date_created__year__lt=1950).update(date_created=None)


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0174_auto_20231119_0748'),
    ]

    operations = [
            migrations.RunPython(convert_old_dates_to_null),
    ]
