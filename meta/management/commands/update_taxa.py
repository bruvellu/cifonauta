# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils import translation
from django.template.defaultfilters import slugify
from meta.models import Media, Taxon
from worms import Aphia

# TODO: taxa_update.py: Fetch data and status from WoRMS
# TODO: taxa_update.py: Fetch data and status from WoRMS

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

    def handle(self, *args, **options):

        # Set language to Portuguese by default
        translation.activate('pt-br')

        # Parse options
        n = options['number']
        days = options['days']
        rank = options['rank']
        print(options)

        # TODO: Outline
        # 1. Fetch taxa filtering by timestamp, rank, and number
        # 2. Search taxon name in WoRMS
        # 3. Parse search results (one or more matches)
        # 4. Update taxon record and status
        # 5. Add/update higher ranks from taxon
        # 6. Fetch whole hierarchical tree

        # Get all taxa
        taxa = Taxon.objects.all()
        # Ignore recently updated taxa
        if days:
            today = timezone.now()
            datelimit = today - timezone.timedelta(days=days)
            taxa = taxa.filter(timestamp__lt=datelimit)
        # Only update taxa of a specific rank
        if rank:
            taxa = taxa.filter(rank_en=rank)
        # Limit the total number of taxa
        taxa = taxa[:n]

        # Connect to WoRMS webservice
        if taxa:
            self.aphia = Aphia()

        # Loop over taxa
        for taxon in taxa:
            records = self.search_worms(taxon.name)
            if not records:
                continue
            # Trust first best hit from WoRMS
            record = records[0]
            self.update_taxon(taxon, record)

            #record = self.get_valid_taxon(records)

            #TODO: Continue from here

    def search_worms(self, taxon_name):
        '''Search WoRMS for taxon name.'''
        records = self.aphia.get_aphia_records(taxon_name)
        if not records:
            return None
        return records

    def update_taxon(self, taxon, record):
        '''Update taxon entry in the database.'''
        print(taxon.__dict__)
        fields = {
                'name': record['scientificname'],
                'slug': slugify(record['scientificname']),
                'rank_en': record['rank'],
                'rank_pt_br': EN2PT[record['rank']],
                'aphia': record['AphiaID'],
                'timestamp': timezone.now(),
                }
        taxon.update(**fields)
        print(taxon.__dict__)
        #taxon.save()

    def get_valid_taxon(self, records):
        '''Get a single valid taxon from records.'''
        if record['status'] == 'accepted':
            return record
        else:
            valid = self.aphia.get_aphia_record_by_id(record['valid_AphiaID'])
            # valid = search_worms(record['valid_name'])
            return valid


    # def print_record(self, record):
        # '''Print string with taxon information.'''
        # self.stdout.write('{0}: {1} {2} ({3}) > {4}'.format(
            # record['AphiaID'],
            # record['scientificname'],
            # record['authority'],
            # record['rank'],
            # record['status']))


        # All media taxa.
        # all_taxa = list(media.values_list('taxon__name', flat=True))
        # print(all_taxa)

        # for taxon_name in all_taxa:
            # if taxon_name:
                # self.stdout.write('\nInitiating search on: {}'.format(taxon_name))
                # # Get valid record.
                # record = search_worms(taxon_name)
                # if record:
                    # self.stdout.write('\nBest match record: {0} ({1}) -- {2}'.format(
                        # record['scientificname'],
                        # record['rank'],
                        # record['status'])
                        # )
                    # # Get model.
                    # taxon = Taxon.objects.get(name=taxon_name)
                    # # Update it with the new information.
                    # update_model(taxon, record)
                    # self.stdout.write('Saved!')
                # else:
                    # self.stdout.write('No record in WoRMS: {}'.format(taxon_name))

#            if taxon.rank_pt_br and taxon.rank_en:
#                continue
#            elif not taxon.rank_pt_br or not taxon.rank_en:
#                taxon.rank_en = translate_rank(taxon.rank_pt_br)
#                taxon.rank_pt_br = translate_rank(taxon.rank_en)
#                taxon.save()
#            else:
#                continue
#
#        self.stdout.write('Finished translation.')





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


def get_best_match(query):
    '''Searches and finds best-matching valid WoRMS record.'''
    records = self.get_aphia_records(query)
    if not records:
        # TODO Elaborate search with fuzzy match_aphia_records_by_names.
        return None
    for record in records:
        if record['status'] == 'accepted':
            return record
        elif record['status'] == 'unaccepted' or record['status'] == 'alternate representation':
            valid = self.get_best_match(record['valid_name'])
    return valid


def translate_rank(rank):
   '''Translate ranks intelligently.'''

   pt2en = {
           'Subforma': 'Subform',
           'Superordem': 'Superorder',
           'Variedade': 'Variety',
           'Infraordem': 'Infraorder',
           'Seção': 'Section',
           'Subclasse': 'Subclass',
           'Subseção': 'Subsection',
           'Reino': 'Kingdom',
           'Infrareino': 'Infrakingdom',
           'Divisão': 'Division',
           'Subtribo': 'Subtribe',
           'Aberração': 'Aberration',
           'Infraordem': 'InfraOrder',
           'Subreino': 'Subkingdom',
           'Infraclasse': 'Infraclass',
           'Subfamília': 'Subfamily',
           'Classe': 'Class',
           'Superfamília': 'Superfamily',
           'Subdivisão': 'Subdivision',
           'Morfotipo': 'Morph',
           'Raça': 'Race',
           'Não especificado': 'Unspecified',
           'Subordem': 'Suborder',
           'Gênero': 'Genus',
           'Ordem': 'Order',
           'Subvariedade': 'Subvariety',
           'Tribo': 'Tribe',
           'Subgênero': 'Subgenus',
           'Forma': 'Form',
           'Família': 'Family',
           'Subfilo': 'Subphylum',
           'Estirpe': 'Stirp',
           'Filo': 'Phylum',
           'Superclasse': 'Superclass',
           'Subespécie': 'Subspecies',
           'Espécie': 'Species',
           }

   en2pt = {
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
           }

   try:
       rank_translation = en2pt[rank]
       return rank_translation
   except:
       try:
           rank_translation = pt2en[rank]
           return rank_translation
       except:
           return rank
   else:
       return rank

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
        }
