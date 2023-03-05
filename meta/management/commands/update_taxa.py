from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils import translation
from django.template.defaultfilters import slugify
from meta.models import Media, Taxon
from worms import Aphia


# TODO: Taxonomic names are not unique
# Cidaroida
# [INFO] 2023-03-04 23:12:17,919 @ worms get_aphia_record_by_id (l107): Searching for the ID "510498"
# [INFO] 2023-03-04 23:12:18,655 @ worms print_record (l208): Found: 510498 / Cidaroidea / Smith, 1984 / Subclass / accepted
# [INFO] 2023-03-04 23:12:18,667 @ worms print_record (l208): Saved: 510498 / Cidaroidea / Smith, 1984 / Subclass / accepted
# Cidaridae
# [INFO] 2023-03-04 23:12:18,672 @ worms get_aphia_record_by_id (l107): Searching for the ID "852318"
# [INFO] 2023-03-04 23:12:19,397 @ worms print_record (l208): Found: 852318 / Cidaroidea / Gray, 1825 / Superfamily / accepted

#TODO: Maybe just simplify and use the canonical ranks

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

Salariinae
Parablennius
Steenstrupiella steenstrupii
Codonellidae
Tintinnopsis
Dictyocysta
Dictyocysta reticulata
Epiplocylis
Epiplocylididae
Ascampbelliella aperta
Gobiesocoidei
Canthigaster figueiredoi
Stephanolepis hispidus
Balistes vetula
Scorpaena plumieri
Janolidae
Janolus
Janolus mucloc
Chromodoris paulomarcioi
Anomalocardia brasiliana
Nephasoma pellucidum
Themiste alutacea
Muraenidae
Muraeninae
Dactylopteroidei
Dactylopteridae
Dactylopterus
Blennioidei
Labrisomidae
Parablennius marmoreus
Halichoeres poeyi
Chromis
Chromis multilineata
Halichoeres
Haemulon plumieri
Sparidae
Diplodus
Stephanolepis
Balistidae
Balistes
Ogcocephalidae
Ogcocephalus
Ogcocephalus vespertilio

for id in taxa.values('id'):
 t = Taxon.objects.get(id=id['id'])
 t.parent = None
 try:
  t.save()
 except:
  print(t)

for id in taxa.values('id'):
 t = Taxon.objects.get(id=id['id'])
 t.level = 0
 try:
  t.save()
 except:
  print(t)

for id in taxa.values('id'):
 t = Taxon.objects.get(id=id['id'])
 t.move_to(None)
 try:
  t.save()
 except:
  print(t)
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
        parser.add_argument('--no-aphia', action='store_true', dest='no_aphia',
                help='Only search for taxa without AphiaID.')
        parser.add_argument('--only-aphia', action='store_true', dest='only_aphia',
                help='Only search for taxa with AphiaID.')
        parser.add_argument('-p', '--parent', action='store_true', dest='parent_get',
                help='Also fetch parent taxon.')

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
        no_aphia = options['no_aphia']
        only_aphia = options['only_aphia']
        parent_get = options['parent_get']

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
        if no_aphia:
            taxa = taxa.filter(aphia=None)
        elif only_aphia:
            taxa = taxa.filter(aphia__isnull=False)

        # Limit the total number of taxa
        taxa = taxa[:n]

        # Connect to WoRMS webservice
        if taxa:
            self.aphia = Aphia()

        # Loop over taxon queryset
        for taxon in taxa:
            print(taxon.name)

            # Skip over taxa already with an AphiaID
            if not taxon.aphia:

                # Search taxon name in WoRMS
                records = self.search_worms(taxon.name)

                # Skip taxon without record (but update timestamp)
                if not records:
                    taxon.save()
                    continue

                # Trust first best hit from WoRMS (seems good)
                record = records[0]

                # Skip match without proper name (but update timestamp)
                if taxon.name != record['scientificname']:
                    taxon.save()
                    continue

                # Update database entry with new informations
                taxon = self.update_taxon(taxon, record)

            # Get parent of the taxon
            if parent_get and taxon.parent_aphia:
                parent = self.get_parent(taxon)
                taxon.parent = parent
                taxon.save()

    def search_worms(self, taxon_name):
        '''Search WoRMS for taxon name.'''
        records = self.aphia.get_aphia_records(taxon_name)
        if not records:
            return None
        return records

    def update_taxon(self, taxon, record):
        '''Update taxon entry in the database.'''
        # Convert status string to boolean
        if record['status'] == 'accepted':
            is_valid = True
        else:
            is_valid = False
        # Handle Biota None rank
        if not record['rank']:
            rank_en = ''
            rank_pt_br = ''
        else:
            rank_en = record['rank']
            rank_pt_br = EN2PT[record['rank']]

        # Set new data for individual fields
        taxon.name = record['scientificname']
        taxon.authority = record['authority']
        taxon.is_valid = is_valid
        taxon.slug = slugify(record['scientificname'])
        taxon.rank_en = rank_en
        taxon.rank_pt_br = rank_pt_br
        taxon.aphia = record['AphiaID']
        taxon.parent_aphia = record['parentNameUsageID']
        taxon.save()
        self.aphia.print_record(record, pre='Saved: ')
        return taxon

    def get_parent(self, taxon):
        '''Get or create the parent of a taxon.'''
        try:
            parent = Taxon.objects.get(aphia=taxon.parent_aphia)
        except Taxon.DoesNotExist:
            record = self.aphia.get_aphia_record_by_id(taxon.parent_aphia)
            self.aphia.print_record(record, pre='Found: ')
            parent, new = Taxon.objects.get_or_create(name=record['scientificname'])
            parent = self.update_taxon(parent, record)
        return parent

    def get_valid_taxon(self, records):
        '''Get a single valid taxon from records.'''
        if record['status'] == 'accepted':
            return record
        else:
            valid = self.aphia.get_aphia_record_by_id(record['valid_AphiaID'])
            # valid = search_worms(record['valid_name'])
            return valid


# DEPRECATED
def update_model(taxon, record):
    '''Updates database entry.'''
    today = timezone.now()
    taxon.name = record['scientificname']
    taxon.slug = slugify(record['scientificname'])
    taxon.rank_en = record['rank']
    taxon.rank_pt_br = translate_rank(record['rank'])
    taxon.aphia = record['AphiaID']
    taxon.timestamp = today
    taxon.save()

    # Keep instances for saving parent hierarchy.
    instances = [taxon]

    # Get parents' instances.
    parents = [
            {'name': record['genus'], 'rank': 'Genus'},
            {'name': record['family'], 'rank': 'Family'},
            {'name': record['order'], 'rank': 'Order'},
            {'name': record['cls'], 'rank': 'Class'},
            {'name': record['phylum'], 'rank': 'Phylum'},
            {'name': record['kingdom'], 'rank': 'Kingdom'},
            ]
    for parent in parents:
        if parent['name'] and not parent['name'] == record['scientificname']:
            # Get instance first.
            parent_instance, new = Taxon.objects.get_or_create(name=parent['name'])
            # Only search WoRMS if last update was > a week ago.
            if parent_instance.timestamp:
                difference = today - parent_instance.timestamp
                delta_days = difference.days
            else:
                delta_days = 10
            if new or delta_days > 7:
                parent_record = search_worms(parent['name'])
                parent_instance.name = parent_record['scientificname']
                parent_instance.rank_en = parent_record['rank']
                parent_instance.rank_pt_br = translate_rank(parent_record['rank'])
                parent_instance.aphia = parent_record['AphiaID']
                parent_instance.timestamp = today
                parent_instance.save()
            instances.append(parent_instance)

    # Iterate through instances saving parents.
    previous = None
    for instance in instances:
        if previous:
            previous.parent = instance
            previous.save()
            print('{0} ({1}) -> {2} ({3})'.format(
                previous.name, previous.rank_en,
                instance.name, instance.rank_en,
                ))
        previous = instance


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
