# Generated by Django 4.2.11 on 2024-04-07 17:12

from django.db import migrations, models
import meta.models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0221_alter_country_name_alter_country_name_en_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='file_large',
            field=models.FileField(default=None, help_text='Arquivo processado tamanho grande.', max_length=200, null=True, upload_to=meta.models.user_upload_directory),
        ),
    ]
