# Generated by Django 4.2.1 on 2023-08-07 15:03

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meta', '0077_alter_curadoria_curators_alter_curadoria_specialists'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curadoria',
            name='curators',
            field=models.ManyToManyField(blank=True, help_text='Curadores da curadoria.', related_name='curatorship_curator', to=settings.AUTH_USER_MODEL, verbose_name='curadores'),
        ),
        migrations.AlterField(
            model_name='curadoria',
            name='specialists',
            field=models.ManyToManyField(blank=True, help_text='Especialistas da curadoria.', related_name='curatorship_specialist', to=settings.AUTH_USER_MODEL, verbose_name='especialistas'),
        ),
    ]
