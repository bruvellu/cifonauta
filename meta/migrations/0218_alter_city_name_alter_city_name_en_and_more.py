# Generated by Django 4.2.11 on 2024-04-07 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0217_auto_20240217_0741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='city',
            name='name',
            field=models.CharField(help_text='Nome da cidade.', max_length=64, verbose_name='nome'),
        ),
        migrations.AlterField(
            model_name='city',
            name='name_en',
            field=models.CharField(help_text='Nome da cidade.', max_length=64, null=True, verbose_name='nome'),
        ),
        migrations.AlterField(
            model_name='city',
            name='name_pt_br',
            field=models.CharField(help_text='Nome da cidade.', max_length=64, null=True, verbose_name='nome'),
        ),
    ]
