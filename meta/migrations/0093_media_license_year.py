# Generated by Django 4.2.3 on 2023-08-21 23:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0092_alter_media_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='license_year',
            field=models.CharField(blank=True, default='0000', help_text='Ano da licença escolhida', max_length=4, verbose_name='Ano da Licença'),
        ),
    ]
