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
                            help='Number of media to update (default=10, max=1000).')

        parser.add_argument('--days', type=int, default=1,
                            help='Skip entries updated less than X days ago (default=1).')

        parser.add_argument('--hours', type=int, default=0,
                            help='Skip entries updated less than X hours ago (default=0).')

        parser.add_argument('--minutes', type=int, default=0,
                            help='Skip entries updated less than X minutes ago (default=0).')
        parser.add_argument('--only-photo', action='store_true', dest='only_photo',
                help='Only update photos.')

        parser.add_argument('--only-video', action='store_true', dest='only_video',
                help='Only update videos.')

        parser.add_argument('--skip-recent', action='store_true', dest='skip_recent',
                help='Skip media updated recently (last day).')

    def handle(self, *args, **options):

        # Print options
        print()
        for k, v in options.items():
            print(f'  {k}: {v}')
        print()

        # Parse options
        id = options['id']
        number = options['number']
        days = options['days']
        hours = options['hours']
        minutes = options['minutes']
        only_photo = options['only_photo']
        only_video = options['only_video']
        skip_recent = options['skip_recent']

        # Start with all media files
        media = Media.objects.all()

        # Only photos
        if only_photo:
            media = media.filter(datatype='photo')

        # Only videos
        if only_video:
            media = media.filter(datatype='video')

        # Ignore recently updated files
        if skip_recent:
            datelimit = timezone.now() - timezone.timedelta(
                    days=days,
                    hours=hours,
                    minutes=minutes
                    )
            media = media.filter(date_modified__lt=datelimit)

        # Limit the total number of taxa
        if number > 1000:
            print(f'You requested {number} entries, but the limit is 1000.')
            number = 1000
        media = media[:number]

        # If ID, ignore above and force processing
        if id:
            media = Media.objects.filter(id=id)
            print(f'Processing single file ID={id} (ignoring other filters).')
        else:
            print(f'Processing {number} files...')
            print(f'photo={only_photo}, video={only_video}, recent={skip_recent}')

        # Loop over taxon queryset
        for instance in media:
            print(instance.id, instance.file)
            instance.resize_files()
            instance.close_files()

