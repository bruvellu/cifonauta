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

        parser.add_argument('--id', type=int, default=None,
                            help='ID of the media to update.')

        parser.add_argument('-n', '--number', type=int, default=10,
                            help='Number of media to update (default=10).')

        parser.add_argument('--days', type=int, default=1,
                            help='Skip entries updated less than X days ago (default=1).')

        parser.add_argument('--hours', type=int, default=0,
                            help='Skip entries updated less than X hours ago (default=0).')

        parser.add_argument('--minutes', type=int, default=0,
                            help='Skip entries updated less than X minutes ago (default=0).')
        parser.add_argument('--only-photos', action='store_true', dest='only_photos',
                help='Only update photos.')

        parser.add_argument('--only-videos', action='store_true', dest='only_videos',
                help='Only update videos.')

        parser.add_argument('--skip-recent', action='store_true', dest='skip_recent',
                help='Skip media updated recently (last day).')

    def handle(self, *args, **options):

        # Parse options
        id = options['id']
        number = options['number']
        days = options['days']
        hours = options['hours']
        minutes = options['minutes']
        only_photos = options['only_photos']
        only_videos = options['only_videos']
        skip_recent = options['skip_recent']

        # Start with all media files
        media = Media.objects.all()

        # Only photos
        if only_photos:
            media = media.filter(datatype='photo')

        # Only videos
        if only_videos:
            media = media.filter(datatype='video')

        # Ignore recently updated files
        if skip_recent:
            datelimit = timezone.now() - timezone.timedelta(
                    days=days,
                    hours=hours,
                    minutes=minutes)
            media = media.filter(date_modified__lt=datelimit)

        # Limit the total number of taxa
        media = media[:number]

        # If ID, ignore above and force processing
        if id:
            media = Media.objects.filter(id=id)
            print(f'\nProcessing single file ID={id} (ignoring other filters).')
        else:
            print(f'\nProcessing {number} files...')

        # Print options
        print()
        for k, v in options.items():
            ignore = ['settings', 'verbosity', 'pythonpath', 'traceback',
                      'no_color', 'force_color', 'skip_checks', 'number']
            if not id:
                ignore.append('id')
            if not skip_recent:
                ignore.extend(['days', 'hours', 'minutes'])
            if not k in ignore:
                print(f'  {k}: {v}')
        print()

        # Loop over taxon queryset, closing files when done
        for instance in media:
            print(instance.id, instance.file)
            instance.resize_files()
            instance.close_files()

