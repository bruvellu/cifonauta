# Generated by Django 4.2.1 on 2023-07-29 16:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import meta.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meta', '0068_curadoria'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='author',
            field=models.ForeignKey(help_text='Autor da mídia.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='autor'),
        ),
        migrations.AddField(
            model_name='media',
            name='curadoria',
            field=models.ForeignKey(help_text='Curadoria à qual a imagem pertence.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='meta.curadoria', verbose_name='curadoria'),
        ),
        migrations.AddField(
            model_name='media',
            name='file',
            field=models.FileField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='media',
            name='status',
            field=models.CharField(blank=True, choices=[('not_edited', 'Não Editado'), ('to_review', 'Para Revisão'), ('published', 'Publicado')], default='not_edited', help_text='Status da mídia.', max_length=13, verbose_name='status'),
        ),
    ]
