# Generated by Django 4.2.1 on 2023-11-25 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0188_alter_media_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modifiedmedia',
            name='date',
        ),
        migrations.AddField(
            model_name='modifiedmedia',
            name='date_created',
            field=models.DateTimeField(blank=True, help_text='Data de criação do arquivo.', null=True, verbose_name='data de criação'),
        ),
    ]