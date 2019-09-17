# Generated by Django 2.2.5 on 2019-09-14 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0033_auto_20190914_1345'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tagcategory',
            options={'ordering': ['name'], 'verbose_name': 'categoria de marcadores', 'verbose_name_plural': 'categorias de marcadores'},
        ),
        migrations.RemoveField(
            model_name='tagcategory',
            name='parent',
        ),
        migrations.RemoveField(
            model_name='tagcategory',
            name='position',
        ),
        migrations.AlterField(
            model_name='tagcategory',
            name='description',
            field=models.TextField(blank=True, default='', help_text='Descrição da categoria de marcadores.', verbose_name='descrição'),
        ),
        migrations.AlterField(
            model_name='tagcategory',
            name='description_en',
            field=models.TextField(blank=True, default='', help_text='Descrição da categoria de marcadores.', null=True, verbose_name='descrição'),
        ),
        migrations.AlterField(
            model_name='tagcategory',
            name='description_pt_br',
            field=models.TextField(blank=True, default='', help_text='Descrição da categoria de marcadores.', null=True, verbose_name='descrição'),
        ),
        migrations.AlterField(
            model_name='tagcategory',
            name='slug',
            field=models.SlugField(blank=True, default='', help_text='Slug do nome da categoria de marcadores.', max_length=64, verbose_name='slug'),
        ),
    ]