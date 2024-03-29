# Generated by Django 4.2.7 on 2024-01-10 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0208_remove_modifiedmedia_specialist_person'),
    ]

    operations = [
        migrations.AddField(
            model_name='reference',
            name='doi',
            field=models.CharField(blank=True, help_text='DOI da referência', max_length=40, verbose_name='doi'),
        ),
        migrations.AddField(
            model_name='reference',
            name='metadata',
            field=models.JSONField(blank=True, help_text='Metadados da referência', null=True, verbose_name='Metadados'),
        ),
    ]
