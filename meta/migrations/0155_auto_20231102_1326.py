# Generated by Django 4.2.3 on 2023-11-02 16:26

from django.db import migrations

def migrate_tag_data(apps, schema_editor):
    '''Migrate Media data from tag_set to tags.'''

    Media = apps.get_model('meta', 'Media')

    for media in Media.objects.all():

        media.tags.set(media.tag_set.all())

        media.save()

class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0154_remove_person_is_author'),
    ]

    operations = [
            migrations.RunPython(migrate_tag_data),
    ]
