# Generated by Django 4.2.3 on 2023-09-29 03:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0118_alter_media_tag_life_stage_test'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='tag_life_stage_test',
            field=models.ForeignKey(limit_choices_to={'category': 'estagio-de-vida'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='life_stage_test', to='meta.tag', verbose_name='Estágio de Vida'),
        ),
    ]
