# Generated by Django 4.2.1 on 2023-09-05 12:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0108_alter_person_email_alter_person_orcid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='city',
            field=models.ForeignKey(help_text='Cidade mostrada na imagem (ou cidade de coleta).', null=True, on_delete=django.db.models.deletion.SET_NULL, to='meta.city', verbose_name='cidade'),
        ),
        migrations.AlterField(
            model_name='media',
            name='country',
            field=models.ForeignKey(help_text='País mostrado na imagem (ou país de coleta).', null=True, on_delete=django.db.models.deletion.SET_NULL, to='meta.country', verbose_name='país'),
        ),
        migrations.AlterField(
            model_name='media',
            name='date',
            field=models.DateTimeField(help_text='Data de criação da imagem.', null=True, verbose_name='data'),
        ),
        migrations.AlterField(
            model_name='media',
            name='state',
            field=models.ForeignKey(help_text='Estado mostrado na imagem (ou estado de coleta).', null=True, on_delete=django.db.models.deletion.SET_NULL, to='meta.state', verbose_name='estado'),
        ),
    ]
