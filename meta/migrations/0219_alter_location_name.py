# Generated by Django 4.2.11 on 2024-04-07 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0218_alter_city_name_alter_city_name_en_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='name',
            field=models.CharField(help_text='Nome da localidade.', max_length=64, verbose_name='nome'),
        ),
    ]
