# Generated by Django 2.2.28 on 2023-03-03 22:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0057_auto_20191201_1101'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name'], 'verbose_name': 'categoria', 'verbose_name_plural': 'categorias'},
        ),
        migrations.AlterModelOptions(
            name='country',
            options={'ordering': ['name'], 'verbose_name': 'país', 'verbose_name_plural': 'países'},
        ),
        migrations.AlterModelOptions(
            name='stats',
            options={'verbose_name': 'estatísticas', 'verbose_name_plural': 'estatísticas'},
        ),
        migrations.AlterField(
            model_name='person',
            name='media',
            field=models.ManyToManyField(blank=True, help_text='Arquivos associados a este autor.', to='meta.Media', verbose_name='arquivos'),
        ),
        migrations.AlterField(
            model_name='reference',
            name='media',
            field=models.ManyToManyField(blank=True, help_text='Arquivos associados a esta referência.', to='meta.Media', verbose_name='arquivos'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='category',
            field=models.ForeignKey(blank=True, help_text='Categoria associada a este marcador.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tags', to='meta.Category', verbose_name='categorias'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='media',
            field=models.ManyToManyField(blank=True, help_text='Arquivos associados a este marcador.', to='meta.Media', verbose_name='arquivos'),
        ),
        migrations.AlterField(
            model_name='taxon',
            name='aphia',
            field=models.PositiveIntegerField(blank=True, help_text='AphiaID, o identificador do táxon no WoRMS.', null=True),
        ),
        migrations.AlterField(
            model_name='taxon',
            name='media',
            field=models.ManyToManyField(blank=True, help_text='Arquivos associados a este táxon.', to='meta.Media', verbose_name='arquivos'),
        ),
        migrations.AlterField(
            model_name='taxon',
            name='timestamp',
            field=models.DateTimeField(auto_now=True, help_text='Data da última modificação do arquivo.', null=True, verbose_name='data de modificação'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='media',
            field=models.ManyToManyField(blank=True, help_text='Arquivos associados a este tour.', to='meta.Media', verbose_name='arquivos'),
        ),
    ]
