# Generated by Django 4.2.1 on 2023-08-07 13:54

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meta', '0073_curadoria_taxons'),
    ]

    operations = [
        migrations.AddField(
            model_name='curadoria',
            name='curators',
            field=models.ManyToManyField(help_text='Curadores da curadoria.', null=True, related_name='curatorship_curator', to=settings.AUTH_USER_MODEL, verbose_name='curadores'),
        ),
    ]