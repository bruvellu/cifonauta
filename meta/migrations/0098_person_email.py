# Generated by Django 4.2.1 on 2023-08-28 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0096_alter_media_terms'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='email',
            field=models.EmailField(max_length=254, null=True, verbose_name='Email'),
        ),
    ]
