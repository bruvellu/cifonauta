import os
import pickle
import re

from django.template.defaultfilters import slugify

from meta.models import Taxon
from utils.worms import Aphia

# TODO: Also fetch non-marine species

"""
Library for updating taxonomic information in the Cifonauta database using the
worms.py library.

Usage:
>>> from utils.taxa import TaxonUpdater
>>> taxon_updater = TaxonUpdater('Acanthostracion polygonius')
>>> taxon_updater.name
'Acanthostracion polygonius'
>>> taxon_updater.processed_records
[<TaxonRecord: Acanthostracion polygonius>]
"""


class TaxonRecord:
    """Handle processing of individual taxon records."""

    def __init__(self, record, updater):
        """
        Initialize with a WoRMS record and reference to the parent updater.

        Parameters:
        - record: WoRMS record dictionary
        - updater: Reference to parent TaxonUpdater for cache access, etc.
        """
        self.record = record
        self.updater = updater
        self.taxon = None
        self.check = None
        self.lineage = None
        self.valid_taxon = None
        self.valid_record = None
        self.valid_lineage = None
        self.status = "pending"

    def __str__(self):
        """Return string representation of taxon record."""
        return self.record["scientificname"]

    def process(self, lineage=True):
        """Execute full processing pipeline for this taxon record."""
        # Get or create database entry using AphiaID for uniqueness
        self.taxon = self.get_or_create_taxon()

        # Update database with record data
        self.check = self.update_taxon_metadata()

        # Stop update if check fails
        if not self.check:
            return False

        # Create taxonomic lineage (by default)
        if lineage:
            self.lineage = self.save_taxon_lineage()

        # Process valid taxon if needed
        self.process_valid_taxon()

        return True

    def get_or_create_taxon(self):
        """Get or create Taxon instance using name and AphiaID."""
        aphia_id = self.record["AphiaID"]
        taxon_name = self.record["scientificname"]

        # Get taxon instance using name and AphiaID
        taxon, is_new = Taxon.objects.get_or_create(
            name__iexact=taxon_name,
            aphia=aphia_id,
            defaults={"name": taxon_name, "aphia": aphia_id},
        )
        print(f"Taxon: {taxon} (new={is_new})")
        return taxon

    def check_taxon_record(self):
        """Check WoRMS record name against Taxon name, they should be identical."""
        # Skip taxon without exact name match
        # TODO: Figure out what to do in this situation
        if self.record["scientificname"] != self.taxon.name:
            print(
                f'Record name mismatch: "{self.record["scientificname"]}" not identical to "{self.taxon.name}"'
            )
            # self.status = "absent"
            return False

        return True

    def update_taxon_metadata(self):
        """Update taxon entry in the database."""
        # Check taxon record
        check = self.check_taxon_record()

        # If record broken, only save taxon object
        if not check:
            # Updates timestamp
            self.taxon.save()
            print(f"Saved: {self.taxon} (without WoRMS metadata)")
            return False

        # Set new metadata for individual fields
        self.taxon.aphia = self.record["AphiaID"]
        self.taxon.name = self.record["scientificname"]
        self.taxon.authority = self.record["authority"]
        self.taxon.status_en = self.record["status"]
        self.taxon.status_pt_br = self.updater.translate_status(self.record["status"])
        self.taxon.is_valid = self.set_status(self.record["status"])
        self.taxon.slug = slugify(self.record["scientificname"])
        self.taxon.rank_en = self.record["rank"]
        self.taxon.rank_pt_br = self.updater.translate_rank(self.record["rank"])
        self.taxon.citation = self.record["citation"]

        # Save taxon and return
        self.taxon.save()
        print(f"Saved: {self.taxon} (with WoRMS metadata)")
        return True

    def set_status(self, record_status):
        """Set status based on record status."""
        if record_status == "accepted":
            self.status = "accepted"
            return True
        else:
            self.status = "invalid"
            return False

    def get_full_taxon_lineage(self):
        """Get full taxonomic lineage of this taxon."""
        # Initial list for lineage tree
        lineage = [self.taxon]

        # Save current record
        current_record = self.record

        # Iterate up the tree, appending to lineage, updating record
        while current_record["parentNameUsageID"] != 1:
            # Get parent record
            parent_record = self.updater.get_worms_record_by_id(
                current_record["parentNameUsageID"]
            )

            # Create parent taxon record and process it
            parent_taxon_record = TaxonRecord(parent_record, self.updater)
            parent_taxon_record.process(lineage=False)

            # Add parent to lineage
            lineage.append(parent_taxon_record.taxon)
            # Update current record to parent record
            current_record = parent_record

        # Reverse list to start with higher ranks
        lineage.reverse()
        return lineage

    def save_taxon_lineage(self):
        """Get or create parent taxa and set tree relationship."""
        # Get list with taxon lineage, including itself
        lineage = self.get_full_taxon_lineage()

        if len(lineage) > 1:
            print(f"Lineage:")

        # Establish parent > child relationships
        for count, parent in enumerate(lineage):
            # Last taxon's parent already set on previous iteration
            if count == len(lineage) - 1:
                print(f" [{parent.rank_en}] {parent} (valid={parent.is_valid})")
                break

            # Get child of current taxon (parent)
            child = lineage[count + 1]
            print(f" [{parent.rank_en}] {parent} (valid={parent.is_valid})")
            # print(
                # f" [{parent.rank_en}] {parent} (valid={parent.is_valid}) > {child} (valid={child.is_valid})"
            # )

            # Skip setting itself as parent
            if parent.name == child.name:
                continue

            # Set parent for child
            child.parent = parent
            # Update timestamp
            child.save()

        return lineage

    def process_valid_taxon(self):
        """Get valid taxon name and ancestors if needed."""
        if not self.taxon.is_valid and self.record["valid_AphiaID"]:
            print(f"Invalid: {self.taxon}")
            print(f"Searching for the valid equivalent...")

            # Get valid record
            valid_record = self.updater.get_worms_record_by_id(
                self.record["valid_AphiaID"]
            )

            # Create and process valid taxon record
            valid_taxon_record = TaxonRecord(valid_record, self.updater)
            valid_taxon_record.process()

            # Store references
            self.valid_taxon = valid_taxon_record.taxon
            self.valid_record = valid_record
            self.valid_lineage = valid_taxon_record.lineage

            # Link invalid taxon to its valid equivalent
            self.taxon.valid_taxon = self.valid_taxon
            self.taxon.save()

            print(f"Linked invalid {self.taxon} to valid {self.valid_taxon}")

            return True
        return False


class TaxonUpdater:
    """Manage taxonomic information of taxa using WoRMS."""

    def __init__(self, taxon_name=""):
        """
        Initialize with WoRMS web service.

        Parameters:
        - name: Initial taxon name to querying records
        """
        # Connect to WoRMS web service
        self.aphia = Aphia()

        # Instantiate variables
        self.taxon_name = taxon_name
        self.cached_records = {}
        self.cache_file = "worms.pkl"
        self.fetched_records = []
        self.returned_taxa = []

        # Load cache
        self.load_cache_from_file()

        # Execute update pipeline
        if self.taxon_name:
            self.update(taxon_name)

    def update(self, taxon_name):
        """Execute update pipeline for given taxon name."""
        # Clean input name
        self.taxon_name = self.sanitize_name(taxon_name)

        # First get all matching records
        self.fetched_records = self.find_records_by_taxon_name(self.taxon_name)

        # Process each record individually
        for record in self.fetched_records:
            taxon_record = TaxonRecord(record, self)
            taxon_record.process()
            self.returned_taxa.append(taxon_record)

        # Write updated cache to file
        self.write_cache_to_file()

        # Return the fetched_records
        return self.returned_taxa

    def find_records_by_taxon_name(self, taxon_name):
        """Fetch records with taxon name from cache or worms."""

        # Try first finding matches on cache
        records_from_cache = self.get_records_from_cache(taxon_name)
        if records_from_cache:
            print(f"Found {len(records_from_cache)} records for {taxon_name} on cache")
            return records_from_cache
        else:
            print(f"No records found for {taxon_name} on cache")

        # Try second finding matches on WoRMS
        records_from_worms = self.get_records_from_worms(taxon_name)
        if records_from_worms:
            print(f"Found {len(records_from_worms)} records for {taxon_name} on WoRMS")
            return records_from_worms
        else:
            print(f"No records found for {taxon_name} on WoRMS")

        # Without matches, return empty list
        return []

    def get_records_from_cache(self, taxon_name):
        """Find all records with matching scientific name in cache."""
        print(f"Searching cache for {taxon_name}")
        matching_records = []
        for aphia_id, record in self.cached_records.items():
            if record["scientificname"] == taxon_name:
                matching_records.append(record)
        return matching_records

    def get_records_from_worms(self, taxon_name):
        """Find all records with matching scientific name on WoRMS."""
        print(f"Searching WoRMS for {taxon_name}")
        matching_records = []

        worms_results = self.aphia.get_aphia_records(taxon_name)

        if not worms_results:
            return matching_records

        # Process and filter records
        for record in worms_results:
            if record["scientificname"] == taxon_name:
                record_dict = self.convert_suds_to_dict(record)
                self.add_record_to_cache(record_dict)
                matching_records.append(record_dict)

        return matching_records

    def get_worms_record_by_id(self, aphia_id):
        """Get WoRMS taxon record by AphiaID."""
        # TODO: Add option to ignore cache
        try:
            # Try getting record from cache
            record = self.cached_records[aphia_id]
            print(f'Cache: {record["scientificname"]} (id={aphia_id})')
            return record
        except KeyError:
            # Not in cache, get from WoRMS
            record = self.aphia.get_aphia_record_by_id(aphia_id)
            # Convert to dictionary and save to cache
            if record:
                record = self.convert_suds_to_dict(record)
                self.add_record_to_cache(record)
                return record
            return None

    def load_cache_from_file(self):
        """Load a pickle file with previously fetched WoRMS records."""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "rb") as file:
                    self.cached_records = pickle.load(file)
                print(
                    f"Loaded: {len(self.cached_records)} WoRMS records from {self.cache_file}"
                )
            else:
                print(f"Note: {self.cache_file} was not found")
        except Exception as e:
            print(f"Error loading records: {str(e)}")
            self.cached_records = {}

    def write_cache_to_file(self):
        """Write fetched WoRMS records to pickle file."""
        try:
            with open(self.cache_file, "wb") as file:
                pickle.dump(self.cached_records, file)
            print(
                f"Saved: {len(self.cached_records)} WoRMS records to {self.cache_file}"
            )
        except Exception as e:
            print(f"Error saving records: {str(e)}")

    def add_record_to_cache(self, record):
        """Add record to dictionary with fetched records."""
        aphia_id = record["AphiaID"]
        self.cached_records[aphia_id] = record

    def convert_suds_to_dict(self, record):
        """Convert AphiaRecord suds object to standard dictionary."""
        return self.aphia.client.dict(record)

    def sanitize_name(self, name):
        """Trim spaces and standardize case for input names."""
        # General rule standard names like: Clypeaster subdepressus
        sanitized = name.strip().lower().capitalize()
        # Special case for cases like: Echinaster (Othilia) brasiliensis
        sanitized = re.sub(
            r"\((\w+)\)", lambda m: f"({m.group(1).capitalize()})", sanitized
        )
        if sanitized != name:
            print(f'Sanitized: "{name}" to "{sanitized}"')
        return sanitized

    def translate_status(self, status_en):
        """Translate status from English to Portuguese."""
        # Dictionary of taxonomic status for translations
        en2pt_statuses = {
            "accepted": "aceito",
            "unreplaced junior homonym": "homônimo júnior não substituído",
            "unaccepted": "não aceito",
            "nomen nudum": "nomen nudum",
            "interim unpublished": "provisoriamente não publicado",
            "superseded combination": "combinação substituída",
            "junior homonym": "homônimo júnior",
            "junior subjective synonym": "sinônimo subjetivo júnior",
            "junior objective synonym": "sinônimo objetivo júnior",
            "nomen oblitum": "nomen oblitum",
            "misspelling - incorrect original spelling": "erro ortográfico - grafia original incorreta",
            "misspelling - incorrect subsequent spelling": "erro ortográfico - grafia subsequente incorreta",
            "unjustified emendation": "emenda injustificada",
            "incorrect grammatical agreement of specific epithet": "concordância gramatical incorreta do epíteto específico",
            "misapplication": "aplicação incorreta",
            "unavailable name": "nome indisponível",
            "superseded rank": "categoria taxonômica substituída",
            "alternative representation": "representação alternativa",
            "temporary name": "nome temporário",
            "uncertain": "incerto",
            "nomen dubium": "nomen dubium",
            "taxon inquirendum": "taxon inquirendum",
            "unassessed": "não avaliado",
        }

        # Return empty string if status has no translation
        try:
            return en2pt_statuses[status_en]
        except:
            print(f"{status_en} has no translation.")
            return ""

    def translate_rank(self, rank_en):
        """Translate rank from English to Portuguese."""

        # Dictionary of taxonomic ranks for translations
        en2pt_ranks = {
            "Class": "Classe",
            "Epifamily": "Epifamília",
            "Family": "Família",
            "Forma": "Forma",
            "Genus": "Gênero",
            "Gigaclass": "Gigaclasse",
            "Infraclass": "Infraclasse",
            "Infrakingdom": "Infrareino",
            "Infraorder": "Infraordem",
            "Infraphylum": "Infrafilo",
            "Kingdom": "Reino",
            "Megaclass": "Megaclasse",
            "Mutatio": "Mutatio",
            "Natio": "Natio",
            "Order": "Ordem",
            "Parvorder": "Parvordem",
            "Parvphylum": "Parvfilo",
            "Phylum": "Filo",
            "Phylum (Division)": "Filo (Divisão)",
            "Section": "Seção",
            "Species": "Espécie",
            "Subclass": "Subclasse",
            "Subfamily": "Subfamília",
            "Subforma": "Subforma",
            "Subgenus": "Subgênero",
            "Subkingdom": "Subreino",
            "Suborder": "Subordem",
            "Subphylum": "Subfilo",
            "Subphylum (Subdivision)": "Subfilo (Subdivisão)",
            "Subsection": "Subseção",
            "Subspecies": "Subespécie",
            "Subterclass": "Subterclasse",
            "Subtribe": "Subtribo",
            "Subvariety": "Subvariedade",
            "Superclass": "Superclasse",
            "Superfamily": "Superfamília",
            "Superorder": "Superordem",
            "Superphylum": "Superfilo",
            "Supertribe": "Supertribo",
            "Tribe": "Tribo",
            "Variety": "Variedade",
            "Aberration": "Aberração",
            "Division": "Divisão",
            "Morph": "Morfotipo",
            "Race": "Raça",
            "Stirp": "Estirpe",
            "Subdivision": "Subdivisão",
            "Superdomain": "Superdomínio",
            "Unspecified": "Não especificado",
        }

        # Return empty string if rank has no translation
        try:
            return en2pt_ranks[rank_en]
        except:
            print(f"{rank_en} has no translation.")
            return ""
