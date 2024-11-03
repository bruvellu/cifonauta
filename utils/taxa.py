import os
import pickle
import re

from django.template.defaultfilters import slugify

from meta.models import Taxon
from utils.worms import Aphia

# TODO: Also fetch non-marine species

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
    '''Manage taxonomic information of taxa using WoRMS.'''

    def __init__(self, name=''):
        '''Without a name, only initialize web service.'''

        # Connect to WoRMS web service
        self.aphia = Aphia()

        # Execute update pipeline
        if name:
            self.update(name)

    def update(self, name):
        '''Execute update pipeline for given taxon name.'''

        # Clean input name
        self.name = self.sanitize_name(name)

        # Taxon status on WoRMS: accepted, invalid, or absent
        self.status = 'absent'

        # Cache dictionary for fetched records
        self.cache = 'worms.pkl'
        self.records = {}
        self.namemap = {}
        self.load_cache_from_file()

        # Disable MPTT updates
        # Taxon.objects.disable_mptt_updates()

        # Get Taxon instance and WoRMS record
        self.taxon, self.record = self.get_taxon_record_by_name(self.name)

        # Update database entry with new record data
        self.taxon, self.check = self.update_taxon(self.taxon, self.record)

        # Stop update in case of missing record or mismatch
        if not self.check:
            return None

        # Get or create parent taxa
        self.lineage = self.save_taxon_lineage(self.taxon, self.record)

        # Get valid taxon if needed
        self.valid_taxon, self.valid_record, self.valid_lineage = self.get_valid_taxon(self.taxon, self.record)

        # Write cache to file
        self.write_cache_to_file()

    def rebuild_hierarchy(self):
        '''Rebuild tree hierarchy of taxa.'''
        # Rebuild tree hierarchy
        Taxon.objects.rebuild()

    def sanitize_name(self, name):
        '''Trim spaces and standardize case for input names.'''
        # General rule standard names like: Clypeaster subdepressus
        sanitized = name.strip().lower().capitalize()
        # Special case for cases like: Echinaster (Othilia) brasiliensis
        sanitized = re.sub(r'\((\w+)\)', lambda m: f'({m.group(1).capitalize()})', sanitized)
        if sanitized != name:
            print(f'Sanitized: "{name}" to "{sanitized}"')
        return sanitized

    def load_cache_from_file(self):
        '''Load a pickle file with previously fetched WoRMS records.'''
        try:
            if os.path.exists(self.cache):
                with open(self.cache, 'rb') as file:
                    self.records = pickle.load(file)
                self.namemap = {record['scientificname']: aphia for aphia, record in self.records.items()}
                print(f'Loaded: {len(self.records.keys())} WoRMS records from {self.cache}')
            else:
                print(f'Note: {self.cache} was not found')
        except Exception as e:
            print(f'Error loading records from {self.cache}: {str(e)}')
            self.records = {}

    def write_cache_to_file(self):
        '''Write fetched WoRMS records to pickle file.'''
        try:
            with open(self.cache, 'wb') as file:
                pickle.dump(self.records, file)
            print(f'Saved: {len(self.records.keys())} WoRMS records to {self.cache}')
        except Exception as e:
            print(f'Error saving records to {self.cache}: {str(e)}')

    def convert_suds_to_dict(self, record):
        '''Convert AphiaRecord suds object to standard dictionary.'''
        record = self.aphia.client.dict(record)
        return record

    def add_record_to_cache(self, record):
        '''Add record to dictionary with fetched records.'''
        self.namemap[record['scientificname']] = record['AphiaID']
        self.records[record['AphiaID']] = record

    def get_or_create_taxon(self, name):
        '''Get or create Taxon instance passing default name.'''
        taxon, is_new = Taxon.objects.get_or_create(name__iexact=name, defaults={'name': name})
        print(f'Taxon: {taxon} (new={is_new})')
        return taxon

    def get_worms_record_by_id(self, aphia):
        '''Get WoRMS taxon record by AphiaID.'''
        #TODO: Add option to ignore cache
        try:
            # Try getting record from cache
            record = self.records[aphia]
            print(f'Cache: {record["scientificname"]}')
        except:
            # Get from WoRMS, convert to dictionary, save to cache
            record = self.aphia.get_aphia_record_by_id(aphia)
            record = self.convert_suds_to_dict(record)
            self.add_record_to_cache(record)

        # Return empty if something goes wrong
        if not record:
            return None
        return record

    def get_worms_record_by_name(self, taxon_name):
        '''Search WoRMS for taxon name and return the first matching record.'''
        #TODO: Add option to ignore cache
        try:
            # Try getting record from cache
            record = self.records[self.namemap[taxon_name]]
            print(f'Cache: {record["scientificname"]}')
            return record
        except:
            # Search WoRMS for name
            records = self.aphia.get_aphia_records(taxon_name)
            if not records:
                return None
            # Return the first non-empty, generally it's the best match
            for record in records:
                if record['scientificname']:
                    record = self.convert_suds_to_dict(record)
                    self.add_record_to_cache(record)
                    return record
                else:
                    return None

    def check_taxon_record(self, taxon, record):
        '''Check WoRMS record name against Taxon name, they should be identical.'''

        # Skip taxon without WoRMS record (but update timestamp)
        if not record:
            print(f'Record not found: No WoRMS record for "{taxon.name}"')
            self.status = 'absent'
            return False

        # Skip taxon without exact name match (but update timestamp)
        if record['scientificname'] != taxon.name:
            print(f'Record name mismatch: "{record["scientificname"]}" (WoRMS) not identical to "{taxon.name}" (Taxon name)')
            self.status = 'absent'
            return False

        # If not caught above
        return True

    def update_taxon(self, taxon, record):
        '''Update taxon entry in the database.'''

        # Check taxon record
        check = self.check_taxon_record(taxon, record)

        # If record broken or absent, only save taxon object
        if not check:
            # Updates timestamp
            taxon.save()
            print(f'Saved: {taxon} (without WoRMS metadata)')
        else:
            taxon = self.update_metadata(taxon, record)

        return taxon, check

    def set_status(self, record_status):
        '''Set self.status based on record['status'].'''
        if record_status == 'accepted':
            self.status = 'accepted'
            return True
        else:
            self.status = 'invalid'
            return False

    def update_metadata(self, taxon, record):
        '''Update taxon metadata with WoRMS record data.'''

        # Set new metadata for individual fields
        taxon.aphia = record['AphiaID']
        taxon.name = record['scientificname']
        taxon.authority = record['authority']
        taxon.status_en = record['status']
        taxon.status_pt_br = self.translate_status(record['status'])
        taxon.is_valid = self.set_status(record['status'])
        taxon.slug = slugify(record['scientificname'])
        taxon.rank_en = record['rank']
        taxon.rank_pt_br = self.translate_rank(record['rank'])
        taxon.citation = record['citation']

        # Save taxon and return
        taxon.save()
        print(f'Saved: {taxon} (with WoRMS metadata)')

        return taxon

    def translate_status(self, status_en):
        '''Translate status from English to Portuguese.'''

        # Dictionary of taxonomic status for translations
        en2pt_statuses = {
                'accepted': 'aceito',
                'unreplaced junior homonym': 'homônimo júnior não substituído',
                'unaccepted': 'não aceito',
                'nomen nudum': 'nomen nudum',
                'interim unpublished': 'provisoriamente não publicado',
                'superseded combination': 'combinação substituída',
                'junior homonym': 'homônimo júnior',
                'junior subjective synonym': 'sinônimo subjetivo júnior',
                'junior objective synonym': 'sinônimo objetivo júnior',
                'nomen oblitum': 'nomen oblitum',
                'misspelling - incorrect original spelling': 'erro ortográfico - grafia original incorreta',
                'misspelling - incorrect subsequent spelling': 'erro ortográfico - grafia subsequente incorreta',
                'unjustified emendation': 'emenda injustificada',
                'incorrect grammatical agreement of specific epithet': 'concordância gramatical incorreta do epíteto específico',
                'misapplication': 'aplicação incorreta',
                'unavailable name': 'nome indisponível',
                'superseded rank': 'categoria taxonômica substituída',
                'alternative representation': 'representação alternativa',
                'temporary name': 'nome temporário',
                'uncertain': 'incerto',
                'nomen dubium': 'nomen dubium',
                'taxon inquirendum': 'taxon inquirendum',
                'unassessed': 'não avaliado'
                }


        # Return empty string if status has no translation 
        try:
            status_pt = en2pt_statuses[status_en]
        except:
            print(f'{status_en} has no translation.')
            status_pt = ''

        return status_pt

    def translate_rank(self, rank_en):
        '''Translate rank from English to Portuguese.'''

        # Dictionary of taxonomic ranks for translations
        en2pt_ranks = {
                'Class': 'Classe',
                'Epifamily': 'Epifamília',
                'Family': 'Família',
                'Forma': 'Forma',
                'Genus': 'Gênero',
                'Gigaclass': 'Gigaclasse',
                'Infraclass': 'Infraclasse',
                'Infrakingdom': 'Infrareino',
                'Infraorder': 'Infraordem',
                'Infraphylum': 'Infrafilo',
                'Kingdom': 'Reino',
                'Megaclass': 'Megaclasse',
                'Mutatio': 'Mutatio',
                'Natio': 'Natio',
                'Order': 'Ordem',
                'Parvorder': 'Parvordem',
                'Parvphylum': 'Parvfilo',
                'Phylum': 'Filo',
                'Phylum (Division)': 'Filo (Divisão)',
                'Section': 'Seção',
                'Species': 'Espécie',
                'Subclass': 'Subclasse',
                'Subfamily': 'Subfamília',
                'Subforma': 'Subforma',
                'Subgenus': 'Subgênero',
                'Subkingdom': 'Subreino',
                'Suborder': 'Subordem',
                'Subphylum': 'Subfilo',
                'Subphylum (Subdivision)': 'Subfilo (Subdivisão)',
                'Subsection': 'Subseção',
                'Subspecies': 'Subespécie',
                'Subterclass': 'Subterclasse',
                'Subtribe': 'Subtribo',
                'Subvariety': 'Subvariedade',
                'Superclass': 'Superclasse',
                'Superfamily': 'Superfamília',
                'Superorder': 'Superordem',
                'Superphylum': 'Superfilo',
                'Supertribe': 'Supertribo',
                'Tribe': 'Tribo',
                'Variety': 'Variedade',
                'Aberration': 'Aberração',
                'Division': 'Divisão',
                'Morph': 'Morfotipo',
                'Race': 'Raça',
                'Stirp': 'Estirpe',
                'Subdivision': 'Subdivisão',
                'Superdomain': 'Superdomínio',
                'Unspecified': 'Não especificado'
                }

        # Return empty string if rank has no translation 
        try:
            rank_pt = en2pt_ranks[rank_en]
        except:
            print(f'{rank_en} has no translation.')
            rank_pt = ''

        return rank_pt

    def get_taxon_record_by_name(self, name):
        '''Get taxon object and WoRMS record by scientific name.'''
        taxon = self.get_or_create_taxon(name)
        record = self.get_worms_record_by_name(taxon.name)
        return taxon, record

    def get_taxon_record_by_id(self, aphia):
        '''Get WoRMS record by AphiaID and create taxon object.'''
        record = self.get_worms_record_by_id(aphia)
        taxon = self.get_or_create_taxon(record['scientificname'])
        return taxon, record

    def get_canonical_taxon_lineage(self, taxon, record):
        '''Get canonical taxonomic lineage of a taxon.'''

        # Initial list for lineage tree
        lineage = [taxon]

        # Canonical ranks from WoRMS
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
                parent_taxon, parent_record = self.get_taxon_record_by_name(parent_name)

                parent_taxon, parent_check = self.update_taxon(parent_taxon, parent_record)
                lineage.append(parent_taxon)

        # Reverse list to start with higher ranks
        lineage.reverse()

        return lineage

    def get_full_taxon_lineage(self, taxon, record):
        '''Get full taxonomic lineage of a taxon.'''

        # Initial list for lineage tree
        lineage = [taxon]

        # Save current record
        current_record = record

        # Iterate up the tree, appending to lineage and updating record
        while current_record['parentNameUsageID'] != 1:
            # Get and update parent taxon
            parent_taxon, parent_record = self.get_taxon_record_by_id(current_record['parentNameUsageID'])
            parent_taxon, parent_check = self.update_taxon(parent_taxon, parent_record)
            # Append to lineage and update current record
            lineage.append(parent_taxon)
            current_record = parent_record

        # Reverse list to start with higher ranks
        lineage.reverse()

        return lineage
        
    def save_taxon_lineage(self, taxon, record):
        '''Get or create parent taxa and set tree relationship.'''
        # Get list with taxon lineage, including itself
        # lineage = self.get_canonical_taxon_lineage(taxon, record)
        lineage = self.get_full_taxon_lineage(taxon, record)

        # Establish parent > child relationships
        print(f'Lineage:')
        for count, parent in enumerate(lineage):
            # Last taxon's parent already set on previous iteration
            if count == len(lineage) - 1:
                break

            # Get child of current taxon (parent)
            child = lineage[count + 1]

            print(f' [{parent.rank_en}] {parent} (valid={parent.is_valid}) > {child} (valid={child.is_valid})')

            # Skip setting itself as parent
            if parent.name == child.name:
                continue

            # Remove current parent of child (updates tree)
            # child.move_to(None, 'last-child')
            # Set new parent for child (updates tree)
            # child.move_to(parent, 'last-child')
            # Like this, it doesn't trigger MPTT
            child.parent = parent
            # Saving updates the timestamp
            child.save()

        return lineage

    def get_valid_taxon(self, taxon, record):
        '''Get valid taxon name and ancestors, if needed.'''
        if not taxon.is_valid and record['valid_AphiaID']:
            print(f'Invalid: {taxon}')
            print(f'Searching for the valid equivalent...')

            # Get valid record and taxon and save instance
            valid_taxon, valid_record = self.get_taxon_record_by_id(record['valid_AphiaID'])
            valid_taxon, valid_check = self.update_taxon(valid_taxon, valid_record)

            # Save lineage for valid taxon
            valid_lineage = self.save_taxon_lineage(valid_taxon, valid_record)

            # Add valid_taxon reference to invalid taxon
            taxon.valid_taxon = valid_taxon
            taxon.save()

            # Mirror associated images
            # No longer needed, done on pre_save at meta/signals.py
            # valid_taxon.media.add(*taxon.media.all())
            # valid_taxon.save()

            print(f'Saved: {valid_taxon} (valid={valid_taxon.is_valid}) over {taxon} (valid={taxon.is_valid})')
            return valid_taxon, valid_record, valid_lineage
        else:
            return False, False, False

