from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from meta.models import Taxon
from utils.taxa import TaxonUpdater


class Command(BaseCommand):
    args = ''
    help = 'Update taxonomic records in batch.'

    def add_arguments(self, parser):

        parser.add_argument('-n', '--number', type=int, default=10,
                            help='Set number of taxa to update (default=10).')

        parser.add_argument('-d', '--days', type=int, default=None,
                help='Only update taxa not updated for this number of days.')

        parser.add_argument('-r', '--rank', default='',
                help='Only update taxa of a specific rank (English).')

        parser.add_argument('--only-aphia', action='store_true', dest='only_aphia',
                help='Only search for taxa with AphiaID.')

        parser.add_argument('--only-orphans', action='store_true', dest='only_orphans',
                help='Only update taxa without parents.')

    def handle(self, *args, **options):

        # Parse options
        n = options['number']
        days = options['days']
        rank = options['rank']
        only_aphia = options['only_aphia']
        only_orphans = options['only_orphans']

        # Get all taxa
        taxa = Taxon.objects.all()

        # Ignore recently updated taxa
        if days:
            datelimit = timezone.now() - timezone.timedelta(days=days)
            taxa = taxa.filter(timestamp__lt=datelimit)

        # Only update taxa of a specific rank
        if rank:
            taxa = taxa.filter(rank_en=rank)

        # Filter only taxa with AphiaID (update existing)
        if only_aphia:
            taxa = taxa.filter(aphia__isnull=False)

        # Filter only taxa without parents
        if only_orphans:
            taxa = taxa.filter(parent__isnull=True)

        # Limit the total number of taxa
        taxa = taxa[:n]

        # Connect to WoRMS webservice
        if not taxa:
            raise CommandError(f'No taxa left after filtering...')

        # Disable MPTT updates
        Taxon.objects.disable_mptt_updates()

        # Loop over taxon queryset
        for taxon in taxa:
            self.stdout.write(taxon.name)

            # Search taxon name in WoRMS
            taxon_updater = TaxonUpdater(taxon.name)

        # Rebuild tree hierarchy
        Taxon.objects.rebuild()

