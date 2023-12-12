# Generated by Django 4.2.1 on 2023-12-12 03:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0200_rename_modifiedmedia2_modifiedmedia'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modifiedmedia',
            options={'verbose_name': 'mídia modificada', 'verbose_name_plural': 'mídias modificadas'},
        ),
        migrations.AlterField(
            model_name='modifiedmedia',
            name='media',
            field=models.OneToOneField(help_text='Mídia original com metadados antes das modificações.', on_delete=django.db.models.deletion.CASCADE, related_name='modified_media', to='meta.media', verbose_name='mídia original'),
        ),
    ]
