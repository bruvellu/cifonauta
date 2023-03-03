# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.template.defaultfilters import slugify
from meta.models import Media, Taxon
from worms import Aphia

'''
Example Aphia record:

(AphiaRecord){
   AphiaID = 106362
   url = "http://www.marinespecies.org/aphia.php?p=taxdetails&id=106362"
   scientificname = "Beroe ovata"
   authority = "Bruguière, 1789"
   rank = "Species"
   status = "accepted"
   unacceptreason = None
   valid_AphiaID = 106362
   valid_name = "Beroe ovata"
   valid_authority = "Bruguière, 1789"
   kingdom = "Animalia"
   phylum = "Ctenophora"
   cls = "Nuda"
   order = "Beroida"
   family = "Beroidae"
   genus = "Beroe"
   citation = "Collins, Allen G. (2010). Beroe ovata Bruguière, 1789. In: Mills, C.E. Internet (1998-present). Phylum Ctenophora: list of all valid species names. Electronic internet document. Accessed through:  World Register of Marine Species at http://www.marinespecies.org/aphia.php?p=taxdetails&id=106362 on 2017-08-12"
   lsid = "urn:lsid:marinespecies.org:taxname:106362"
   isMarine = 1
   isBrackish = 1
   isFreshwater = 0
   isTerrestrial = 0
   isExtinct = None
   match_type = "like"
   modified = "2010-05-28T12:13:23Z"
 }
'''


class Command(BaseCommand):
    args = ''
    help = 'Update taxonomic records in batch.'

    def add_arguments(self, parser):
        parser.add_argument('-n', '--number', type=int, default=10,
                help='Limit the number of taxa to update.')
        parser.add_argument('-r', '--rank', default='',
                help='Limit the rank of taxa to update.')
        # TODO: Option: ignore timestamp (force update)

    def handle(self, *args, **options):

        # Parse options
        n = options['number']
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
        # Filter by rank
        if rank:
            taxa = taxa.filter(rank=rank)
        # Limit the number
        taxa = taxa[:n]

        # Loop over taxa
        for taxon in taxa:
            if not self.needs_update(taxon):
                continue
            records = self.search_worms(taxon.name)
            #TODO: Continue from here

    def search_worms(self, taxon_name):
        '''Search WoRMS for taxon name.'''
        aphia = Aphia()
        records = aphia.get_aphia_records(taxon_name)
        if not records:
            return None
        return records

    def needs_update(self, taxon):
        '''Calculate days from last update before querying WoRMS.'''
        if not taxon.timestamp:
            self.stdout.write(f'{taxon.name} has no timestamp.')
            return True
        today = timezone.now()
        delta_timezone = today - taxon.timestamp
        delta_days = delta_timezone.days
        if delta_days >= 30:
            self.stdout.write(f'Last updated {delta_days} ago. Updating...')
            return True
        else:
            self.stdout.write(f'Recently updated {delta_days} ago. Ignoring...')
            return False

    def get_valid_taxon(self, records):
        '''Get a single valid taxon from records.'''
        record = records[0]

        for record in records:
            print_record(record)
            if record['status'] == 'accepted':
                return record
            else:
                valid = search_worms(record['valid_name'])
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
           u'Subforma': u'Subform',
           u'Superordem': u'Superorder',
           u'Variedade': u'Variety',
           u'Infraordem': u'Infraorder',
           u'Seção': u'Section',
           u'Subclasse': u'Subclass',
           u'Subseção': u'Subsection',
           u'Reino': u'Kingdom',
           u'Infrareino': u'Infrakingdom',
           u'Divisão': u'Division',
           u'Subtribo': u'Subtribe',
           u'Aberração': u'Aberration',
           u'Infraordem': u'InfraOrder',
           u'Subreino': u'Subkingdom',
           u'Infraclasse': u'Infraclass',
           u'Subfamília': u'Subfamily',
           u'Classe': u'Class',
           u'Superfamília': u'Superfamily',
           u'Subdivisão': u'Subdivision',
           u'Morfotipo': u'Morph',
           u'Raça': u'Race',
           u'Não especificado': u'Unspecified',
           u'Subordem': u'Suborder',
           u'Gênero': u'Genus',
           u'Ordem': u'Order',
           u'Subvariedade': u'Subvariety',
           u'Tribo': u'Tribe',
           u'Subgênero': u'Subgenus',
           u'Forma': u'Form',
           u'Família': u'Family',
           u'Subfilo': u'Subphylum',
           u'Estirpe': u'Stirp',
           u'Filo': u'Phylum',
           u'Superclasse': u'Superclass',
           u'Subespécie': u'Subspecies',
           u'Espécie': u'Species',
           }

   en2pt = {
           u'Subform': u'Subforma',
           u'Superorder': u'Superordem',
           u'Variety': u'Variedade',
           u'Infraorder': u'Infraordem',
           u'Section': u'Seção',
           u'Subclass': u'Subclasse',
           u'Subsection': u'Subseção',
           u'Kingdom': u'Reino',
           u'Infrakingdom': u'Infrareino',
           u'Division': u'Divisão',
           u'Subtribe': u'Subtribo',
           u'Aberration': u'Aberração',
           u'InfraOrder': u'Infraordem',
           u'Subkingdom': u'Subreino',
           u'Infraclass': u'Infraclasse',
           u'Subfamily': u'Subfamília',
           u'Class': u'Classe',
           u'Superfamily': u'Superfamília',
           u'Subdivision': u'Subdivisão',
           u'Morph': u'Morfotipo',
           u'Race': u'Raça',
           u'Unspecified': u'Não especificado',
           u'Suborder': u'Subordem',
           u'Genus': u'Gênero',
           u'Order': u'Ordem',
           u'Subvariety': u'Subvariedade',
           u'Tribe': u'Tribo',
           u'Subgenus': u'Subgênero',
           u'Form': u'Forma',
           u'Family': u'Família',
           u'Subphylum': u'Subfilo',
           u'Stirp': u'Estirpe',
           u'Phylum': u'Filo',
           u'Superclass': u'Superclasse',
           u'Subspecies': u'Subespécie',
           u'Species': u'Espécie',
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
