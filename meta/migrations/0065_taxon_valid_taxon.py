# Generated by Django 2.2.28 on 2023-03-06 20:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0064_taxon_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxon',
            name='valid_taxon',
            field=models.ForeignKey(blank=True, help_text='Táxon sinônimo e válido deste táxon.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='synonyms', to='meta.Taxon', verbose_name='válido'),
        ),
    ]
