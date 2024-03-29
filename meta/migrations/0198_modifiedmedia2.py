# Generated by Django 4.2.1 on 2023-12-11 23:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0197_alter_modifiedmedia_city_alter_modifiedmedia_country_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModifiedMedia2',
            fields=[
                ('media_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='meta.media')),
                ('media', models.OneToOneField(help_text='Mídia original com metadados antes das modificações.', on_delete=django.db.models.deletion.CASCADE, related_name='modified_media2', to='meta.media', verbose_name='mídia original')),
            ],
            bases=('meta.media',),
        ),
    ]
