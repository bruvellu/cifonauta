# Generated by Django 4.2.7 on 2023-12-02 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0195_alter_tag_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='geolocation',
            field=models.CharField(blank=True, default='', help_text='Geolocalização no formato sexagesimal (S 23°48\'45" W 45°24\'27").', max_length=25, verbose_name='geolocalização'),
        ),
        migrations.AlterField(
            model_name='media',
            name='latitude',
            field=models.CharField(blank=True, default='', help_text='Latitude onde a imagem foi criada no formato decimal.', max_length=25, verbose_name='latitude'),
        ),
        migrations.AlterField(
            model_name='media',
            name='longitude',
            field=models.CharField(blank=True, default='', help_text='Longitude onde a imagem foi criada no formato decimal.', max_length=25, verbose_name='longitude'),
        ),
    ]
