from django.core.management.base import BaseCommand
from django.utils import timezone
from django.template.defaultfilters import slugify
from meta.models import Media

'''
Generate resized media files.
'''


class Command(BaseCommand):
    args = ''
    help = 'Generate resized media files.'

    def add_arguments(self, parser):

        parser.add_argument('-i', '--id', type=int, default=None,
                            help='ID of the media to update.')

        parser.add_argument('-n', '--number', type=int, default=10,
                            help='Number of media to update (default=10).')

        parser.add_argument('--only-photo', action='store_true', dest='only_photo',
                help='Only update photos.')

        parser.add_argument('--only-video', action='store_true', dest='only_video',
                help='Only update videos.')

        parser.add_argument('--skip-recent', action='store_true', dest='skip_recent',
                help='Skip media updated recently (last day).')

    def handle(self, *args, **options):

        # Parse options
        id = options['id']
        number = options['number']
        only_photo = options['only_photo']
        only_video = options['only_video']
        skip_recent = options['skip_recent']

        # Start with all media files
        files = Media.objects.all()

        # Only photos
        if only_photo:
            files = files.filter(datatype='photo')

        # Only videos
        if only_video:
            files = files.filter(datatype='video')

        # Ignore recently updated files
        if skip_recent:
            datelimit = timezone.now() - timezone.timedelta(days=1)
            files = files.filter(date_modified__lt=datelimit)

        # Limit the total number of taxa
        files = files[:number]

        # If ID, ignore above and force processing
        if id:
            files = Media.objects.filter(id=id)
            print(f'Processing single file ID={id} (ignoring other filters).')
        else:
            print(f'Processing {number} files...')
            print(f'photo={only_photo}, video={only_video}, recent={skip_recent}')

        # Loop over taxon queryset
        for file in files:
            print(file.id, file.file)
            file.resize_files()

