# Generated by Django 4.2.1 on 2023-08-07 13:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0072_alter_media_filepath'),
    ]

    operations = [
        migrations.AddField(
            model_name='curadoria',
            name='taxons',
            field=models.ManyToManyField(blank=True, to='meta.taxon'),
        ),
    ]
