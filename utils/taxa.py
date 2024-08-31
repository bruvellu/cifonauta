from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils import translation
from django.template.defaultfilters import slugify
from meta.models import Taxon
from utils.worms import Aphia

'''
Library for updating taxonomic information in the Cifonauta database using the
worms.py library.

Usage:

    >>> from utils.taxa import TaxonUpdater
    >>> taxon_updater = TaxonUpdater('Acanthostracion polygonius')
    >>> taxon_updater.name
    'Acanthostracion polygonius'
    >>> taxon_updater.taxon
    <Taxon: Acanthostracion polygonius [id=1335]>
    >>> taxon_updater.record
    (AphiaRecord){
       AphiaID = 158919
       url = "https://www.marinespecies.org/aphia.php?p=taxdetails&id=158919"
       scientificname = "Acanthostracion polygonius"
       authority = "Poey, 1876"
       taxonRankID = 220
       rank = "Species"
       status = "unaccepted"
       unacceptreason = None
       valid_AphiaID = 1577312
       valid_name = "Acanthostracion polygonium"
       valid_authority = "Poey, 1876"
       parentNameUsageID = 126237
       kingdom = "Animalia"
       phylum = "Chordata"
       cls = "Teleostei"
       order = "Tetraodontiformes"
       family = "Ostraciidae"
       genus = "Acanthostracion"
       citation = "Froese, R. and D. Pauly. Editors. (2024). FishBase. Acanthostracion polygonius Poey, 1876. Accessed through: World Register of Marine Species at: https://www.marinespecies.org/aphia.php?p=taxdetails&id=158919 on 2024-02-03"
       lsid = "urn:lsid:marinespecies.org:taxname:158919"
       isMarine = 1
       isBrackish = 0
       isFreshwater = 0
       isTerrestrial = 0
       isExtinct = None
       match_type = "like"
       modified = "2023-01-11T08:59:53.383Z"
     }
    >>> taxon_updater.lineage
    [<Taxon: Animalia [id=2494]>, <Taxon: Chordata [id=2581]>, <Taxon: Teleostei [id=1200]>, <Taxon: Tetraodontiformes [id=2593]>, <Taxon: Ostraciidae [id=3230]>, <Taxon: Acanthostracion [id=3229]>, <Taxon: Acanthostracion polygonius [id=1335]>]
    >>> taxon_updater.valid_taxon
    <Taxon: Acanthostracion polygonium [id=3373]>
    >>> taxon_updater.valid_record
    (AphiaRecord){
       AphiaID = 1577312
       url = "https://www.marinespecies.org/aphia.php?p=taxdetails&id=1577312"
       scientificname = "Acanthostracion polygonium"
       authority = "Poey, 1876"
       taxonRankID = 220
       rank = "Species"
       status = "accepted"
       unacceptreason = None
       valid_AphiaID = 1577312
       valid_name = "Acanthostracion polygonium"
       valid_authority = "Poey, 1876"
       parentNameUsageID = 126237
       kingdom = "Animalia"
       phylum = "Chordata"
       cls = "Teleostei"
       order = "Tetraodontiformes"
       family = "Ostraciidae"
       genus = "Acanthostracion"
       citation = "WoRMS (2024). Acanthostracion polygonium Poey, 1876. Accessed at: https://www.marinespecies.org/aphia.php?p=taxdetails&id=1577312 on 2024-02-03"
       lsid = "urn:lsid:marinespecies.org:taxname:1577312"
       isMarine = 1
       isBrackish = None
       isFreshwater = None
       isTerrestrial = 0
       isExtinct = None
       match_type = "exact"
       modified = "2022-04-12T05:48:37.857Z"
     }
    >>> taxon_updater.valid_lineage
    [<Taxon: Animalia [id=2494]>, <Taxon: Chordata [id=2581]>, <Taxon: Teleostei [id=1200]>, <Taxon: Tetraodontiformes [id=2593]>, <Taxon: Ostraciidae [id=3230]>, <Taxon: Acanthostracion [id=3229]>, <Taxon: Acanthostracion polygonium [id=3373]>]
'''

class TaxonUpdater:
    '''Update taxonomic records for a taxon.'''

    def __init__(self, name):

        # Taxon status, ends in string: accepted, invalid or not_exist
        self.status = None
        self.status = 'not_exist'

        # Clean input name
        self.name = self.sanitize_name(name)

        # Get or create Taxon instance
        self.taxon = self.get_or_create_taxon(self.name)

        # Connect to WoRMS webservice
        self.aphia = Aphia()

        # Search taxon name in WoRMS
        self.record = self.search_worms(self.taxon.name)

        # Check WoRMS record before continuing
        self.check = self.check_record(self.taxon.name, self.record)

        # Stop update in case of missing record or mismatch
        if not self.check:
            self.taxon.save()
            print(f'Saved without WoRMS metadata: {self.taxon}')
            return None

        # Update database entry with new record data
        self.taxon = self.update_taxon_metadata(self.taxon, self.record)
        # Get or create parent taxa
        self.lineage = self.save_taxon_lineage(self.taxon, self.record)

        # Get valid taxon if needed
        self.valid_taxon, self.valid_record, self.valid_lineage = self.get_valid_taxon(self.taxon, self.record)

    def sanitize_name(self, name):
        '''Trim spaces and standardize case for input names.'''
        sanitized = name.strip().lower().capitalize()
        if sanitized != name:
            print(f'Sanitized: "{name}" to "{sanitized}"')
        return sanitized

    def get_or_create_taxon(self, name):
        '''Get or create Taxon instance passing default name.'''
        taxon, is_new = Taxon.objects.get_or_create(name__iexact=name, defaults={'name': name})
        print(f'Taxon: {taxon} (new={is_new})')
        return taxon

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

    def check_record(self, taxon_name, record):
        '''Check WoRMS record against Taxon name.'''

        # Skip taxon without WoRMS record (but update timestamp)
        if not record:
            print(f'Record not found: No WoRMS record for "{taxon_name}"')
            self.status = 'not_exist'
            return False

        # Skip taxon without exact name match (but update timestamp)
        if record['scientificname'] != taxon_name:
            print(f'Record name mismatch: "{record["scientificname"]}" (WoRMS) not identical to "{taxon_name}" (Taxon name)')
            self.status = 'not_exist'
            return False

        # If not caught above
        return True

    def update_taxon_metadata(self, taxon, record):
        '''Update taxon entry in the database.'''
        # Convert status string to boolean
        if record['status'] == 'accepted':
            self.status = 'accepted'
            is_valid = True
        else:
            self.status = 'invalid'
            is_valid = False
        # Set new medadata for individual fields
        taxon.name = record['scientificname']
        taxon.authority = record['authority']
        taxon.status = record['status']
        taxon.is_valid = is_valid
        taxon.slug = slugify(record['scientificname'])
        taxon.rank_en = record['rank']
        taxon.rank_pt_br = self.translate_rank(record['rank'])
        taxon.aphia = record['AphiaID']
        taxon.save()
        print(f'Saved with WoRMS metadata: {taxon}')
        return taxon

    def translate_rank(self, rank_en):
        '''Translate rank from English to Portuguese.'''

        # Dictionary of taxonomic ranks for translations
        en2pt_ranks = {'Subform': 'Subforma',
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
                       'Megaclass': 'Megaclasse',}

        rank_pt = en2pt_ranks[rank_en]
        return rank_pt

    def get_parent_taxon(self, parent_name):
        '''Get parent taxon using its name.'''
        taxon = self.get_or_create_taxon(parent_name)
        record = self.search_worms(taxon.name)
        check = self.check_record(parent_name, record)
        if check:
            taxon = self.update_taxon_metadata(taxon, record)
        else:
            taxon.save()
        return taxon

    def save_taxon_lineage(self, taxon, record):
        '''Get or create parent taxa and set tree relationship.'''
        # Initial list for lineage tree
        lineage = [taxon]
        # Only get standard ranks from WoRMS
        parent_names = [record['genus'],
                        record['family'],
                        record['order'],
                        record['cls'],
                        record['phylum'],
                        record['kingdom'],]
        # Loop over parent names and get or create taxon instances
        for parent_name in parent_names:
            if parent_name:
                parent_name = parent_name.replace('[unassigned] ', '')
                parent_taxon = self.get_parent_taxon(parent_name)
                lineage.append(parent_taxon)

        # Reverse list to start with higher ranks
        lineage.reverse()

        # Establish parent > child relationships
        print(f'Tree relationships:')
        for count, parent in enumerate(lineage):
            print(f'[{parent.timestamp}] {parent} ({parent.rank_en})')
            # Last node has no parent, break the loop
            if count == len(lineage) - 1:
                break
            child = lineage[count + 1]
            # When not species, skip setting itself as parent
            if parent.name == child.name:
                continue
            child.parent = parent
            child.save()
        return lineage

    def get_valid_taxon(self, taxon, record):
        '''Get valid taxon name and ancestors, if needed.'''
        if not taxon.is_valid and record['valid_AphiaID']:
            print(f'Invalid taxon: {taxon}')
            print(f'Searching for the valid equivalent...')
            # Get valid record and taxon and save instance
            valid_record = self.aphia.get_aphia_record_by_id(record['valid_AphiaID'])
            valid_taxon = self.get_or_create_taxon(valid_record['scientificname'])
            valid_taxon = self.update_taxon_metadata(valid_taxon, valid_record)
            # Save lineage for valid taxon
            valid_lineage = self.save_taxon_lineage(valid_taxon, valid_record)
            # Add valid_taxon reference to invalid taxon
            taxon.valid_taxon = valid_taxon
            taxon.save()
            # Mirror associated images
            valid_taxon.media.add(*taxon.media.all())
            valid_taxon.save()
            print(f'Saved valid taxon: {valid_taxon} (replaces {taxon})')
            return valid_taxon, valid_record, valid_lineage
        else:
            return False, False, False

