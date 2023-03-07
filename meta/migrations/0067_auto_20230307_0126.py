# Generated by Django 2.2.28 on 2023-03-07 04:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0066_auto_20230307_0033'),
    ]

    operations = [
        migrations.AddField(
            model_name='taxon',
            name='status_en',
            field=models.CharField(blank=True, help_text='Status do táxon.', max_length=256, null=True, verbose_name='status'),
        ),
        migrations.AddField(
            model_name='taxon',
            name='status_pt_br',
            field=models.CharField(blank=True, help_text='Status do táxon.', max_length=256, null=True, verbose_name='status'),
        ),
    ]
