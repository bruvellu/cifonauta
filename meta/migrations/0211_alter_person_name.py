# Generated by Django 4.2.7 on 2024-01-19 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0210_remove_reference_metadata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='name',
            field=models.CharField(blank=True, help_text='Nome do autor.', max_length=200, verbose_name='nome'),
        ),
    ]