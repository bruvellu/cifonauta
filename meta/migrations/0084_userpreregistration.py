# Generated by Django 4.2.1 on 2023-08-10 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0083_alter_media_has_taxons'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPreRegistration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, null=True, verbose_name='Primeiro Nome')),
                ('last_name', models.CharField(max_length=50, null=True, verbose_name='Último Nome')),
                ('orcid', models.CharField(max_length=16, null=True, verbose_name='Orcid')),
            ],
        ),
    ]
