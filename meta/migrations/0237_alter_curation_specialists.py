# Generated by Django 4.2.15 on 2024-09-28 15:34

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meta', '0236_alter_curation_curators_alter_curation_specialists'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curation',
            name='specialists',
            field=models.ManyToManyField(blank=True, help_text='Especialistas nesta curadoria.', related_name='curations_as_specialist', to=settings.AUTH_USER_MODEL, verbose_name='especialistas'),
        ),
    ]
