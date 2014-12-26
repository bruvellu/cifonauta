from django.core.management.base import BaseCommand, CommandError
from meta.models import Image, Video
import pickle
import os


class Command(BaseCommand):
    help = 'Dump unique filenames from database.'

    def handle(self, *args, **options):

        # Get all image paths.
        images = Image.objects.values_list('source_filepath', flat=True)
        self.stdout.write('Compiled %d photos' % images.count())

        # Get all video paths.
        videos = Video.objects.values_list('source_filepath', flat=True)
        self.stdout.write('Compiled %d videos' % videos.count())

        # Merge list of paths.
        unique_paths = list(images) + list(videos)

        # Parse filenames from merged list.
        unique_names = [os.path.basename(path) for path in unique_paths]

        # Dump list to pickled file.
        try:
            pickle.dump(unique_names, open('unique_names.pkl', 'wb'))
            self.stdout.write('Wrote unique_names.pkl')
        except:
            raise CommandError('Failed to write unique_names.pkl')

        self.stdout.write('Dumped %d unique names.' % len(unique_names))
