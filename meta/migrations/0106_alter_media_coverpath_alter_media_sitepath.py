# Generated by Django 4.2.1 on 2023-09-03 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0105_alter_media_coverpath_alter_media_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='coverpath',
            field=models.ImageField(default=None, help_text='Imagem de amostra do arquivo processado.', upload_to='', verbose_name='amostra do arquivo.'),
        ),
        migrations.AlterField(
            model_name='media',
            name='sitepath',
            field=models.FileField(default=None, help_text='Arquivo processado para a web.', upload_to='', verbose_name='arquivo web.'),
        ),
    ]
