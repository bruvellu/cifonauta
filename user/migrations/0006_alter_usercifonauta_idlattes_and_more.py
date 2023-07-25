# Generated by Django 4.2.1 on 2023-07-25 15:14

from django.db import migrations, models
import user.models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0005_usercifonauta_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercifonauta',
            name='idlattes',
            field=models.CharField(max_length=19, null=True, validators=[user.models.idlattes_validator], verbose_name='IDLattes'),
        ),
        migrations.AlterField(
            model_name='usercifonauta',
            name='orcid',
            field=models.CharField(max_length=19, null=True, validators=[user.models.orcid_validator], verbose_name='Orcid'),
        ),
    ]
