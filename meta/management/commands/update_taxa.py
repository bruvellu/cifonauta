from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils import translation
from django.template.defaultfilters import slugify
from meta.models import Media, Taxon
from worms import Aphia

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
                help='Set the number of taxa to update.')
        parser.add_argument('-d', '--days', type=int, default=None,
                help='Only update taxa not updated for this number of days.')
        parser.add_argument('-r', '--rank', default='',
                help='Limit the updates to taxa of a specific rank (English).')
        parser.add_argument('--only-aphia', action='store_true', dest='only_aphia',
                help='Only search for taxa with AphiaID.')

    def handle(self, *args, **options):

        # TODO: taxa_update: fetch taxon infos
        # TODO: taxa_get_parent: fetch parent taxa
        # TODO: taxa_get_valid: find and replace by valid

        # TODO: Also fetch non-marine species

        # Set language to Portuguese by default
        translation.activate('pt-br')

        # Parse options
        n = options['number']
        days = options['days']
        rank = options['rank']
        only_aphia = options['only_aphia']

        # Get all taxa
        taxa = Taxon.objects.all()
        # Ignore recently updated taxa
        if days:
            datelimit = timezone.now() - timezone.timedelta(days=days)
            taxa = taxa.filter(timestamp__lt=datelimit)
        # Only update taxa of a specific rank
        if rank:
            taxa = taxa.filter(rank_en=rank)
        # Filter only taxa without AphiaID
        if only_aphia:
            taxa = taxa.filter(aphia__isnull=False)
        # Limit the total number of taxa
        taxa = taxa[:n]

        # Connect to WoRMS webservice
        if taxa:
            self.aphia = Aphia()

        # Loop over taxon queryset
        for taxon in taxa:
            # Skip over taxa already with an AphiaID
            if not taxon.aphia:
                # Search taxon name in WoRMS
                record = self.search_worms(taxon.name)
                # Skip taxon without record (but update timestamp)
                if not record:
                    taxon.save()
                    continue
                # Skip match without proper name (but update timestamp)
                if taxon.name != record['scientificname']:
                    print(f"{taxon.name} != {record['scientificname']}")
                    taxon.save()
                    continue
                # Update database entry with new informations
                taxon = self.update_taxon(taxon, record)
                # Add/get and link parent taxa
                taxon = self.get_ancestors(taxon, record)

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
        rank_en = record['rank']
        rank_pt_br = EN2PT[record['rank']]
        taxon.aphia = record['AphiaID']
        taxon.save()
        self.aphia.print_record(record, pre='Saved: ')
        return taxon

    def get_ancestors(self, taxon, record):
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
            print(f'{parent}::{child}')
            child.parent = parent
            child.save()

    def get_ancestor(self, name):
        '''Get one parent of a taxon.'''
        taxon, new = Taxon.objects.get_or_create(name=name)
        if new or not taxon.aphia:
            record = self.search_worms(name)
            taxon = self.update_taxon(taxon, record)
        return taxon

    def get_valid_taxon(self, records):
        '''Get a single valid taxon from records.'''
        if record['status'] == 'accepted':
            return record
        else:
            valid = self.aphia.get_aphia_record_by_id(record['valid_AphiaID'])
            # valid = search_worms(record['valid_name'])
            return valid


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
