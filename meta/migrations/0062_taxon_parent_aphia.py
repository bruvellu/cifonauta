# Generated by Django 2.2.28 on 2023-03-03 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0061_taxon_is_valid'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxon',
            name='parent_aphia',
            field=models.PositiveIntegerField(blank=True, help_text='AphiaID do táxon pai.', null=True),
        ),
    ]
