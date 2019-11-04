from django.core.management.base import BaseCommand, CommandError
from meta.models import Media
import os


class Command(BaseCommand):
    help = 'Discover database entries without a media file.'

    def handle(self, *args, **options):
        media = Media.objects.all()

        for i in media:

            if not os.path.isfile(i.filepath):
                self.stdout.write('{}: {}'.format(i, i.filepath))

                delete = input('Delete entry {}? (y/N): '.format(i.id))

                if delete == 'y':
                    i.delete()
