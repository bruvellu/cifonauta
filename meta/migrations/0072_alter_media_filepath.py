# Generated by Django 4.2.1 on 2023-08-01 01:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0071_alter_media_coverpath_alter_media_sitepath'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='filepath',
            field=models.CharField(help_text='Caminho único para arquivo original.', max_length=200, verbose_name='arquivo original.'),
        ),
    ]
