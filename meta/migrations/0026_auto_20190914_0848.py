# Generated by Django 2.2.5 on 2019-09-14 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0025_auto_20190914_0830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, help_text='Data de publicação da imagem no Cifonauta.', verbose_name='data de publicação'),
        ),
    ]
