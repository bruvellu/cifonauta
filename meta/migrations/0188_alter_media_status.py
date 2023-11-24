# Generated by Django 4.2.7 on 2023-11-20 21:07

from django.db import migrations, models


def convert_status_choices(apps, schema_editor):
    '''Convert status choices to new values.'''

    Media = apps.get_model('meta', 'Media')
    Media.objects.filter(is_public=False).filter(status='').update(status='not_edited')
    Media.objects.filter(is_public=True).update(status='published')
    Media.objects.filter(status='not_edited').update(status='draft')
    Media.objects.filter(status='to_review').update(status='submitted')


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0187_alter_media_datatype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='status',
            field=models.CharField(blank=True, choices=[('loaded', 'Carregado'), ('draft', 'Rascunho'), ('submitted', 'Submetido'), ('published', 'Publicado')], default='loaded', help_text='Status da mídia.', max_length=13, verbose_name='status'),
        ),
        migrations.RunPython(convert_status_choices),
    ]