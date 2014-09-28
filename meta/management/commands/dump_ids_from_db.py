from django.core.management.base import BaseCommand, CommandError
from meta.models import Image, Video
import pickle


class Command(BaseCommand):
    help = 'Dump IDs and file paths from database.'

    def handle(self, *args, **options):
        images = Image.objects.all()
        videos = Video.objects.all()

        db_kv = {}
        db_vk = {}

        for i in images:
            photo_id = i.source_filepath.split('/')[-1]
            photo_path = i.old_filepath.split('oficial')[1]
            db_kv[photo_id] = photo_path
            db_vk[photo_path] = photo_id

        self.stdout.write('Compiled %d photos' % images.count())

        for v in videos:
            video_id = v.source_filepath.split('/')[-1]
            video_path = v.old_filepath.split('oficial')[1]
            db_kv[video_id] = video_path
            db_vk[video_path] = video_id

        self.stdout.write('Compiled %d videos' % videos.count())

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

        self.stdout.write('Dumped %d IDs to pickle files.' % len(db_kv.keys()))
