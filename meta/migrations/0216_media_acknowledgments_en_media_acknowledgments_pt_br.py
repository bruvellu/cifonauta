# Generated by Django 4.2.10 on 2024-02-17 10:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0215_media_acknowledgments'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='acknowledgments_en',
            field=models.TextField(blank=True, default='', help_text='Agradecimentos da imagem.', null=True, verbose_name='agradecimentos'),
        ),
        migrations.AddField(
            model_name='media',
            name='acknowledgments_pt_br',
            field=models.TextField(blank=True, default='', help_text='Agradecimentos da imagem.', null=True, verbose_name='agradecimentos'),
        ),
    ]