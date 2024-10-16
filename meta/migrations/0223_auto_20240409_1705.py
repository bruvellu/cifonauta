# Generated by Django 4.2.11 on 2024-04-09 20:05

from django.db import migrations

import os
import shutil


def copy_source_media_to_user_uploads(apps, schema_editor):
    '''Migrate files from source_media to user upload directories.'''

    # Create user upload directories
    UserCifonauta = apps.get_model('user', 'UserCifonauta')
    for user in UserCifonauta.objects.all():
        print(user.id, user.username)
        user_dir = os.path.join('site_media', 'uploads', str(user.id))
        if not os.path.exists(user_dir):
            os.mkdir(user_dir)
            print(f'Created directory {user_dir}')
        else:
            print(f'Directory {user_dir} already exists')

    # Copy original file from source_media
    Media = apps.get_model('meta', 'Media')
    # Absent from source_media
    missing = []
    # for m in Media.objects.filter(id__in=[1,10,100,1000]):
    for m in Media.objects.all():
        print(m.id)
        # Check if file exists
        if not os.path.exists(m.filepath):
            missing.append('{m.id} {m.filepath}')
            print('MISSING: {m.filepath}')
            continue
        # Define new variables
        filename, extension = os.path.splitext(m.filepath)
        newname = f'{m.uuid}{extension.lower()}'
        newfile = os.path.join('uploads', str(m.user.id), newname)
        newpath = os.path.join('site_media', newfile)
        # Copy file
        print(f'FROM: {m.filepath}')
        print(f'  TO: {newpath}')
        shutil.copy(m.filepath, newpath)
        # Update file field
        m.file = newfile
        m.save()
    # Show missing, if any
    if missing:
        print('MISSING:')
        print(missing)
    else:
        print('DONE')


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0222_alter_media_file_large'),
    ]

    operations = [
            migrations.RunPython(copy_source_media_to_user_uploads),
    ]
