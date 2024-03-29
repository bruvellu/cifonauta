# Generated by Django 4.2.1 on 2023-09-05 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0110_merge_20230905_1019'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='co_author',
        ),
        migrations.AlterField(
            model_name='media',
            name='terms',
            field=models.BooleanField(default=False, verbose_name='termos'),
        ),
        migrations.AddField(
            model_name='media',
            name='co_author',
            field=models.ManyToManyField(blank=True, help_text='Coautor(es) da mídia', related_name='co_author', to='meta.person', verbose_name='coautor'),
        ),
    ]
