# Generated by Django 4.2.7 on 2023-11-26 20:09

from django.db import migrations


def migrate_size_tag_to_scale_field(apps, schema_editor):
    '''Migrate data from old size tags to new scale field.'''

    Media = apps.get_model('meta', 'Media')
    Media.objects.filter(tags__name_pt_br='<0,1 mm').update(scale='micro')
    Media.objects.filter(tags__name_pt_br='0,1 - 1,0 mm').update(scale='tiny')
    Media.objects.filter(tags__name_pt_br='1,0 - 10 mm').update(scale='visible')
    Media.objects.filter(tags__name_pt_br='10 - 100 mm').update(scale='large')
    Media.objects.filter(tags__name_pt_br='>100 mm').update(scale='huge')


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0192_media_scale'),
    ]

    operations = [
            migrations.RunPython(migrate_size_tag_to_scale_field),
    ]
