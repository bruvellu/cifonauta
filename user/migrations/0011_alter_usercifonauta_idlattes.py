# Generated by Django 4.2.1 on 2023-08-29 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_delete_userpreregistration'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usercifonauta',
            name='idlattes',
            field=models.CharField(blank=True, max_length=16, null=True, verbose_name='IDLattes'),
        ),
    ]