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
    '''Manage taxonomic information of taxa using WoRMS.'''

    def __init__(self, name):

        # Taxon status on WoRMS: accepted, invalid, or absent
        self.status = 'absent'

        # Clean input name
        self.name = self.sanitize_name(name)

        # Connect to WoRMS webservice
        self.aphia = Aphia()

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

    def get_worms_record_by_id(self, aphia_id):
        '''Get WoRMS taxon record by AphiaID.'''
        record = self.aphia.get_aphia_record_by_id(aphia_id)
        if not record:
            return None
        return record

    def get_worms_record_by_name(self, taxon_name):
        '''Search WoRMS for taxon name and return the first matching record.'''
        records = self.aphia.get_aphia_records(taxon_name)
        if not records:
            return None
        for record in records:
            if record['scientificname']:
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
            print(f'Saved without WoRMS metadata: {taxon}')
        else:
            taxon = self.update_metadata(taxon, record)

        return taxon, check


    def update_metadata(self, taxon, record):
        '''Update taxon metadata with WoRMS record data.'''

        # Convert status string to boolean
        #TODO: turn into function get_boolean_from_status
        if record['status'] == 'accepted':
            self.status = 'accepted'
            is_valid = True
        else:
            self.status = 'invalid'
            is_valid = False

        # Set new metadata for individual fields
        taxon.aphia = record['AphiaID']
        taxon.name = record['scientificname']
        taxon.authority = record['authority']
        taxon.status_en = record['status']
        taxon.status_pt_br = self.translate_status(record['status'])
        taxon.is_valid = is_valid
        taxon.slug = slugify(record['scientificname'])
        taxon.rank_en = record['rank']
        taxon.rank_pt_br = self.translate_rank(record['rank'])
        #TODO: Get record citation into a TextField
        # taxon.citation = record['citation']

        # Save taxon and return
        taxon.save()
        print(f'Saved with WoRMS metadata: {taxon}')
        return taxon

    def translate_status(self, status_en):
        '''Translate status from English to Portuguese.'''

        # Dictionary of taxonomic status for translations
        en2pt_statuses = {
                'accepted': 'aceito',
                'unaccepted': 'não aceito',
                'alternative representation': 'representação alternativa',
                'temporary name': 'nome temporário',
                'uncertain': 'incerto'
                }

        status_pt = en2pt_statuses[status_en]
        return status_pt

    def translate_rank(self, rank_en):
        '''Translate rank from English to Portuguese.'''

        # Dictionary of taxonomic ranks for translations
        en2pt_ranks = {
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
                'Superdomain': 'Superdomínio'
                }

        rank_pt = en2pt_ranks[rank_en]
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
        while current_record.parentNameUsageID != 1:
            # Get and update parent taxon
            parent_taxon, parent_record = self.get_taxon_record_by_id(current_record.parentNameUsageID)
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
        print(f'Lineage tree:')
        for count, parent in enumerate(lineage):
            print(f' [{parent.rank_en}] {parent} (valid={parent.is_valid})')

            # Last taxon's parent already set on previous iteration
            if count == len(lineage) - 1:
                break

            # Get child of current taxon (parent)
            child = lineage[count + 1]

            # Skip setting itself as parent
            if parent.name == child.name:
                continue

            # Save current taxon as the child's parent
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
            valid_taxon = self.update_metadata(valid_taxon, valid_record)

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

