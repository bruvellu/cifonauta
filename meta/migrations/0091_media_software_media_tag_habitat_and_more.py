# Generated by Django 4.2.3 on 2023-08-21 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0090_alter_media_co_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='software',
            field=models.CharField(blank=True, default='', help_text='Software utilizado na Imagem', verbose_name='Software'),
        ),
        migrations.AddField(
            model_name='media',
            name='tag_habitat',
            field=models.CharField(blank=True, default='', help_text='Habitat da imagem', verbose_name='Habitat'),
        ),
        migrations.AddField(
            model_name='media',
            name='tag_life_stage',
            field=models.CharField(blank=True, default='', help_text='Estágio de Vida', verbose_name='Estágio de Vida'),
        ),
        migrations.AddField(
            model_name='media',
            name='tag_lifestyle',
            field=models.CharField(blank=True, default='', help_text='Estilo de vida', verbose_name='Estilo de Vida'),
        ),
        migrations.AddField(
            model_name='media',
            name='tag_microscopy',
            field=models.CharField(blank=True, default='', help_text='Microscópio utilizado', verbose_name='Microscopia'),
        ),
        migrations.AddField(
            model_name='media',
            name='tag_photographic_technique',
            field=models.CharField(blank=True, default='', help_text='Técnica de fotografia utilizada', verbose_name='Técnica de fotografia'),
        ),
        migrations.AddField(
            model_name='media',
            name='tag_several',
            field=models.CharField(blank=True, default='', help_text='Informações diversas', verbose_name='Diversos'),
        ),
    ]