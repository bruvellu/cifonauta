# Generated by Django 4.2.1 on 2023-06-29 16:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_usercifonauta_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='usercifonauta',
            name='orcid',
            field=models.CharField(blank=True, default=None, null=True, unique=True, verbose_name='Orcid'),
        ),
    ]
