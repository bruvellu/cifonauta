# Generated by Django 4.2.7 on 2023-11-19 13:29

from django.db import migrations


def migrate_upload_and_modification_dates(apps, schema_editor):
    '''Migrate timestamp and old pub_date (=date_published) to new date fields.'''

    Media = apps.get_model('meta', 'Media')

    for media in Media.objects.all():

        media.date_uploaded = media.date_published
        media.date_modified = media.timestamp

        media.save()


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0177_media_date_modified_media_date_uploaded'),
    ]

    operations = [
            migrations.RunPython(migrate_upload_and_modification_dates),
    ]
