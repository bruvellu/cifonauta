from django.core.management.base import BaseCommand, CommandError
from meta.models import Image, Video
import pickle


class Command(BaseCommand):
    help = 'Dump IDs and file paths from database.'

    def handle(self, *args, **options):
        media = Media.objects.all()

        db_kv = {}
        db_vk = {}

        for i in media:
            entry_filepath = i.filepath
            entry_sitepath = i.sitepath
            db_kv[entry_filepath] = entry_sitepath
            db_vk[entry_sitepath] = entry_filepath

        self.stdout.write('Compiled {} entries'.format(media.count()))

        try:
            pickle.dump(db_kv, open('db_kv.pkl', 'wb'))
            self.stdout.write('Wrote db_kv.pkl')
        except:
            raise CommandError('Failed to write db_kv.pkl')
        try:
            pickle.dump(db_vk, open('db_vk.pkl', 'wb'))
            self.stdout.write('Wrote db_vk.pkl')
        except:
            raise CommandError('Failed to write db_vk.pkl')

        self.stdout.write('Dumped {} IDs to pickle files.'.format(len(db_kv.keys())))
