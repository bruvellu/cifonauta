from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils import translation
from django.template.defaultfilters import slugify
from meta.models import Taxon
from utils.worms import Aphia

'''
Example Aphia record:

(AphiaRecord){
  AphiaID = 422499
  url = "https://www.marinespecies.org/aphia.php?p=taxdetails&id=422499"
  scientificname = "Clypeaster subdepressus"
  authority = "(Gray, 1825)"
  taxonRankID = 220
  rank = "Species"
  status = "accepted"
  unacceptreason = None
  valid_AphiaID = 422499
  valid_name = "Clypeaster subdepressus"
  valid_authority = "(Gray, 1825)"
  parentNameUsageID = 205242
  kingdom = "Animalia"
  phylum = "Echinodermata"
  cls = "Echinoidea"
  order = "Clypeasteroida"
  family = "Clypeasteridae"
  genus = "Clypeaster"
  citation = "Kroh, A.; Mooi, R. (2023). World Echinoidea Database. Clypeaster subdepressus (Gray, 1825). Accessed through: World Register of Marine Species at: https://www.marinespecies.org/aphia.php?p=taxdetails&id=422499 on 2023-03-02"
  lsid = "urn:lsid:marinespecies.org:taxname:422499"
  isMarine = 1
  isBrackish = 0
  isFreshwater = 0
  isTerrestrial = 0
  isExtinct = 0
  match_type = "like"
  modified = "2013-08-26T18:24:18.240Z"
}
'''


class Command(BaseCommand):
    args = ''
    help = 'Update taxonomic records in batch.'

    def add_arguments(self, parser):

        parser.add_argument('-n', '--number', type=int, default=10,
                            help='Set number of taxa to update (default=10).')

        parser.add_argument('-d', '--days', type=int, default=None,
                help='Only update taxa not updated for this number of days.')

        parser.add_argument('-r', '--rank', default='',
                help='Limit the updates to taxa of a specific rank (English).')

        parser.add_argument('--only-aphia', action='store_true', dest='only_aphia',
                help='Only search for taxa with AphiaID.')

        parser.add_argument('--only-orphans', action='store_true', dest='only_orphans',
                help='Only update taxa without parents.')

        parser.add_argument('--only-new', action='store_true', dest='only_new',
                help='Only update new taxa (without timestamp).')

        parser.add_argument('--force', action='store_true', dest='force',
                help='Force taxon search and update.')

    def handle(self, *args, **options):

        # TODO: Also fetch non-marine species

        # Set language to Portuguese by default
        translation.activate('pt-br')

        # Parse options
        n = options['number']
        days = options['days']
        rank = options['rank']
        only_aphia = options['only_aphia']
        only_orphans = options['only_orphans']
        only_new = options['only_new']
        force = options['force']

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

        # Filter only taxa without timestamp
        if only_new:
            taxa = taxa.filter(timestamp__isnull=True)

        # Filter only taxa without AphiaID, unless forced
        if not force:
            taxa = taxa.filter(aphia__isnull=True)

        # Limit the total number of taxa
        taxa = taxa[:n]

        # Connect to WoRMS webservice
        if taxa:
            self.aphia = Aphia()
        else:
            print('No taxa to search.''')

        # Loop over taxon queryset
        for taxon in taxa:

            print(taxon.name)

            # Search taxon name in WoRMS
            record = self.search_worms(taxon.name)

            # Skip taxon without record (but update timestamp)
            if not record:
                taxon.save()
                continue

            # Skip match without proper name (but update timestamp)
            if taxon.name != record['scientificname']:
                print('{} != {}'.format(taxon.name, record['scientificname']))
                taxon.save()
                continue

            # Update database entry with new record data 
            taxon = self.update_taxon(taxon, record)

            # Add or get, and link parent taxa
            self.save_ancestors(taxon, record)

            # Get valid taxon if needed
            self.get_valid_taxon(taxon, record)

    def search_worms(self, taxon_name):
        '''Search WoRMS for taxon name.'''
        records = self.aphia.get_aphia_records(taxon_name)
        if not records:
            return None
        for record in records:
            if record['scientificname']:
                return record
        else:
            return None

    def update_taxon(self, taxon, record):
        '''Update taxon entry in the database.'''
        # Convert status string to boolean
        if record['status'] == 'accepted':
            is_valid = True
        else:
            is_valid = False
        # Set new data for individual fields
        taxon.name = record['scientificname']
        taxon.authority = record['authority']
        taxon.status = record['status']
        taxon.is_valid = is_valid
        taxon.slug = slugify(record['scientificname'])
        taxon.rank_en = record['rank']
        taxon.rank_pt_br = EN2PT[record['rank']]
        taxon.aphia = record['AphiaID']
        taxon.save()
        self.aphia.print_record(record, pre='Saved: ')
        return taxon

    def save_ancestors(self, taxon, record):
        '''Get and link all parents of a taxon.'''
        lineage = [taxon]
        ancestor_names = [
                record['genus'],
                record['family'],
                record['order'],
                record['cls'],
                record['phylum'],
                record['kingdom'],
                ]
        for name in ancestor_names:
            if name:
                name = name.replace('[unassigned] ', '')
                ancestor = self.get_ancestor(name)
                lineage.append(ancestor)
        lineage.reverse()
        for count, parent in enumerate(lineage):
            # Last node has no parent, break the loop
            if count == len(lineage)-1:
                break
            child = lineage[count+1]
            # When not species, skip setting itself as parent
            if parent.name == child.name:
                continue
            #print(f'{parent}::{child}')
            print('{}::{}'.format(parent, child))
            child.parent = parent
            child.save()

    def get_ancestor(self, name):
        '''Get one parent of a taxon.'''
        taxon, new = Taxon.objects.get_or_create(name=name)
        if new or not taxon.aphia:
            record = self.search_worms(name)
            if record:
                taxon = self.update_taxon(taxon, record)
        return taxon

    def get_valid_taxon(self, taxon, record):
        '''Get valid taxon and ancestors, if needed.'''
        # Get valid taxon
        if not taxon.is_valid and record['valid_AphiaID']:
            # Get valid record and taxon and save instance
            valid_record = self.aphia.get_aphia_record_by_id(record['valid_AphiaID'])
            valid_taxon, new = Taxon.objects.get_or_create(name=valid_record['scientificname'])
            valid_taxon = self.update_taxon(valid_taxon, valid_record)
            # Save ancestors for valid taxon
            self.save_ancestors(valid_taxon, valid_record)
            # Add valid_taxon reference to invalid taxon
            taxon.valid_taxon = valid_taxon
            taxon.save()
            # Mirror associated images
            valid_taxon.media.add(*taxon.media.all())
            valid_taxon.save()

# Dictionary of taxonomic ranks for translations
EN2PT = {
        'Subform': 'Subforma',
        'Superorder': 'Superordem',
        'Variety': 'Variedade',
        'Infraorder': 'Infraordem',
        'Section': 'Seção',
        'Subclass': 'Subclasse',
        'Subsection': 'Subseção',
        'Kingdom': 'Reino',
        'Infrakingdom': 'Infrareino',
        'Division': 'Divisão',
        'Subtribe': 'Subtribo',
        'Aberration': 'Aberração',
        'InfraOrder': 'Infraordem',
        'Subkingdom': 'Subreino',
        'Infraclass': 'Infraclasse',
        'Subfamily': 'Subfamília',
        'Class': 'Classe',
        'Gigaclass': 'Gigaclasse',
        'Superfamily': 'Superfamília',
        'Subdivision': 'Subdivisão',
        'Morph': 'Morfotipo',
        'Race': 'Raça',
        'Unspecified': 'Não especificado',
        'Suborder': 'Subordem',
        'Genus': 'Gênero',
        'Order': 'Ordem',
        'Subvariety': 'Subvariedade',
        'Tribe': 'Tribo',
        'Subgenus': 'Subgênero',
        'Form': 'Forma',
        'Family': 'Família',
        'Subphylum': 'Subfilo',
        'Stirp': 'Estirpe',
        'Phylum': 'Filo',
        'Superclass': 'Superclasse',
        'Subspecies': 'Subespécie',
        'Species': 'Espécie',
        'Parvphylum': 'Parvfilo',
        'Subterclass': 'Subterclasse',
        'Infraphylum': 'Infrafilo',
        'Phylum (Division)': 'Filo (Divisão)',
        'Subphylum (Subdivision)': 'Subfilo (Subdivisão)',
        'Parvorder': 'Parvordem',
        'Megaclass': 'Megaclasse',
        }

