# Generated by Django 2.2.5 on 2019-09-15 08:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0039_auto_20190914_1424'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='city',
            name='image_count',
        ),
        migrations.RemoveField(
            model_name='city',
            name='video_count',
        ),
    ]