# Generated by Django 4.2.1 on 2023-08-11 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0085_media_co_author_alter_media_author'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='co_author',
        ),
        migrations.AddField(
            model_name='media',
            name='co_author',
            field=models.CharField(default='', help_text='Coautor(es) da mídia', max_length=256, verbose_name='coautor'),
        ),
    ]