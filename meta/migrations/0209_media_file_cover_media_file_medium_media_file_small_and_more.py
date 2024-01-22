# Generated by Django 4.2.7 on 2023-12-23 22:38

from django.db import migrations, models
import meta.models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0208_media_file_large_alter_media_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='file_cover',
            field=models.FileField(default=None, help_text='Imagem de capa do arquivo.', null=True, upload_to=meta.models.user_upload_directory),
        ),
        migrations.AddField(
            model_name='media',
            name='file_medium',
            field=models.FileField(default=None, help_text='Arquivo processado tamanho médio.', null=True, upload_to=meta.models.user_upload_directory),
        ),
        migrations.AddField(
            model_name='media',
            name='file_small',
            field=models.FileField(default=None, help_text='Arquivo processado tamanho pequeno.', null=True, upload_to=meta.models.user_upload_directory),
        ),
        migrations.AlterField(
            model_name='media',
            name='file_large',
            field=models.FileField(default=None, help_text='Arquivo processado tamanho grande.', null=True, upload_to=meta.models.user_upload_directory),
        ),
    ]
