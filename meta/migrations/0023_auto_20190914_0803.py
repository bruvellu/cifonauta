# Generated by Django 2.2.5 on 2019-09-14 08:03

from django.db import migrations, models

def copy_data(apps, schema_editor):
    '''From timestamp, datatype, duration, dimensions.'''

    Media = apps.get_model('meta', 'Media')
    media = Media.objects.all()

    Image = apps.get_model('meta', 'Image')
    Video = apps.get_model('meta', 'Video')

    for m in media:
        if m.old_image:
            i = Image.objects.get(id=m.old_image)
            m.timestamp = i.timestamp
            m.datatype = i.datatype
            if not m.datatype:
                m.datatype = 'photo'
            m.save()

        elif m.old_video:
            v = Video.objects.get(id=m.old_video)
            m.timestamp = v.timestamp
            m.datatype = v.datatype
            if not m.datatype:
                m.datatype = 'video'
            m.duration = v.duration
            m.dimensions = v.dimensions
            m.save()

        print(m.timestamp, m.datatype, m.duration, m.dimensions)

class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0022_auto_20190914_0753'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='datatype',
            field=models.CharField(blank=True, help_text='Tipo de mídia.', max_length=15, verbose_name='tipo de mídia'),
        ),
        migrations.AddField(
            model_name='media',
            name='dimensions',
            field=models.CharField(blank=True, default='0x0', help_text='Dimensões do vídeo original.', max_length=20, verbose_name='dimensões'),
        ),
        migrations.AddField(
            model_name='media',
            name='duration',
            field=models.CharField(blank=True, default='00:00:00', help_text='Duração do vídeo no formato HH:MM:SS.', max_length=20, verbose_name='duração'),
        ),
        migrations.AddField(
            model_name='media',
            name='timestamp',
            field=models.DateTimeField(blank=True, help_text='Data da última modificação do arquivo.', null=True, verbose_name='data de modificação'),
        ),
        migrations.RunPython(copy_data, reverse_code=migrations.RunPython.noop),
    ]
