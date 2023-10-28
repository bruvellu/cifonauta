# Generated by Django 4.2.3 on 2023-09-29 03:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0120_alter_media_tag_life_stage_test'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='tag_habitat_test',
            field=models.ForeignKey(limit_choices_to={'category': 8}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='habitat_test', to='meta.tag', verbose_name='Habitat'),
        ),
        migrations.AddField(
            model_name='media',
            name='tag_life_style_test',
            field=models.ForeignKey(limit_choices_to={'category': 8}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='life_style_test', to='meta.tag', verbose_name='Estilo de Vida'),
        ),
        migrations.AddField(
            model_name='media',
            name='tag_microscopy_test',
            field=models.ForeignKey(limit_choices_to={'category': 8}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='microscopy_test', to='meta.tag', verbose_name='Microscópia'),
        ),
        migrations.AddField(
            model_name='media',
            name='tag_photographic_technique_test',
            field=models.ForeignKey(limit_choices_to={'category': 8}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='photographic_technique_test', to='meta.tag', verbose_name='Técnica Fotográfica'),
        ),
        migrations.AddField(
            model_name='media',
            name='tag_several_test',
            field=models.ForeignKey(limit_choices_to={'category': 8}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='several_test', to='meta.tag', verbose_name='Diversos'),
        ),
    ]
