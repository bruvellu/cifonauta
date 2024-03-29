# Generated by Django 4.2.3 on 2023-11-01 15:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meta', '0137_alter_media_authors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='user',
            field=models.ForeignKey(help_text='Usuário que fez o upload do arquivo.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user', to=settings.AUTH_USER_MODEL, verbose_name='usuário do arquivo'),
        ),
    ]
