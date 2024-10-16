# Generated by Django 4.2.15 on 2024-10-06 19:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meta", "0238_alter_curation_curators"),
    ]

    operations = [
        migrations.AddField(
            model_name="curation",
            name="description",
            field=models.TextField(
                blank=True,
                default="",
                help_text="Descrição da curadoria.",
                verbose_name="descrição",
            ),
        ),
        migrations.AddField(
            model_name="curation",
            name="slug",
            field=models.SlugField(
                blank=True,
                default="",
                help_text="Slug do nome da curadoria.",
                max_length=64,
                verbose_name="slug",
            ),
        ),
    ]
