# Generated by Django 4.2.7 on 2024-01-20 20:03

from django.db import migrations


def fix_datatype(apps, schema_editor):
    '''Fix empty datatype fields.'''

    PHOTO_EXTENSIONS = ('tif', 'tiff', 'jpg', 'jpeg', 'png', 'gif')
    VIDEO_EXTENSIONS = ('avi', 'mov', 'mp4', 'ogv', 'dv', 'mpg', 'mpeg', 'flv', 'm2ts', 'wmv')

    Media = apps.get_model('meta', 'Media')

    for media in Media.objects.all():

        if not media.datatype:
            print(media)
            names = [media.sitepath.name, media.file.name]
            for name in names:
                if name.endswith(PHOTO_EXTENSIONS):
                    media.datatype = 'photo'
                elif name.endswith(VIDEO_EXTENSIONS):
                    media.datatype = 'video'
        else:
            continue

        media.save()

class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0212_merge_20240120_1624'),
    ]

    operations = [
            migrations.RunPython(fix_datatype),
    ]
