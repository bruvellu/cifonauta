# Generated by Django 4.2.1 on 2023-08-28 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0099_remove_media_co_author_media_co_author'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='co_author',
            field=models.ManyToManyField(blank=True, help_text='Coautor(es) da mídia', related_name='co_author', to='meta.person', verbose_name='coautor'),
        ),
    ]
