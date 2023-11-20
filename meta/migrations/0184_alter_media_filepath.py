# Generated by Django 4.2.7 on 2023-11-19 22:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0183_alter_media_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='filepath',
            field=models.CharField(blank=True, help_text='Caminho único para o arquivo original.', max_length=200, verbose_name='arquivo original'),
        ),
    ]