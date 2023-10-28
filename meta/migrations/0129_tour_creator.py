# Generated by Django 4.2.1 on 2023-10-26 11:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meta', '0128_alter_loadedmedia_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='tour',
            name='creator',
            field=models.ForeignKey(help_text='Usuário que criou o tour.', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='criador'),
        ),
    ]
