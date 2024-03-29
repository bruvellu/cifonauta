# Generated by Django 4.2.1 on 2023-11-03 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0162_modifiedmedia_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='modifiedmedia',
            name='co_author',
        ),
        migrations.AddField(
            model_name='modifiedmedia',
            name='authors',
            field=models.ManyToManyField(blank=True, help_text='Coautor(es) da mídia', related_name='modified_media_authors', to='meta.person', verbose_name='autores'),
        ),
    ]
