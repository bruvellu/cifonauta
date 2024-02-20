from rest_framework import serializers
from .models import Reference, Taxon, Location, Person, Curadoria
from django.utils.text import slugify

from utils.worms import Aphia


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = '__all__'

    def validate_name(self, value):
        reference = Reference.objects.filter(name=value)
        if reference.exists():
            raise serializers.ValidationError(f'DOI já existe no banco de dados')
        return value

class TaxonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxon
        fields = '__all__'

    def save(self):

        self._RANKS_NAMES = {
                    'Kingdom': 'Reino',
                    'Subkingdom': 'Subreino',
                    'Phylum': 'Filo',
                    'Subphylum': 'Subfilo',
                    'Infraphylum': 'Infrafilo',
                    'Megaclass': 'Megaclasse',
                    'Superclass': 'Superclasse',
                    'Class': 'Classe',
                    'Subclass': 'Subclasse',
                    'Infraclass': 'Infraclasse',
                    'Superorder': 'Superordem',
                    'Order': 'Ordem',
                    'Suborder': 'Subordem',
                    'Infraorder': 'Infraordem',
                    'Section': 'Seção',
                    'Subsection': 'Subseção',
                    'Superfamily': 'Superfamília',
                    'Family': 'Família',
                    'Subfamily': 'Subfamília',
                    'Tribe': 'Tribo',
                    'Genus': 'Gênero',
                    'Species': 'Espécie',
                    'Subspecies': 'Subespécie',
                    'Forma': 'Forma'
                    }
        taxon_name = self.validated_data['name']
        records = Aphia().get_aphia_records(taxon_name)

        if len(records)==0:
            Curadoria.objects.get_or_create(name='Sem Aphia')
            parent_taxon_name = "Sem Aphia"
        else:
            parent_taxon_name = self._update_parents_taxon(taxon_name)
            Taxon.objects.rebuild()
        super().save()
        return parent_taxon_name

    def _update_parents_taxon(self, taxon_name):
        #Trecho referente à taxon base
        aphia = Aphia()
        record_taxon = aphia.get_aphia_records(taxon_name)[0]
        parent_name = aphia.get_aphia_name_by_id(record_taxon.parentNameUsageID)
        #Criação do pai da base
        parent_taxon, created = Taxon.objects.get_or_create(name=parent_name)
        #Trecho referento ao pai da taxon base
        if created:
            with Taxon.objects.disable_mptt_updates():
                record_parent_taxon = aphia.get_aphia_records(taxon_name)[0]
                parent_taxon.aphia = record_parent_taxon.AphiaID
                parent_taxon.authority = record_parent_taxon.authority
                if record_parent_taxon.rank in self._RANKS_NAMES.keys():
                    parent_taxon.rank = self._RANKS_NAMES[record_parent_taxon.rank]
                else:
                    parent_taxon.rank = record_parent_taxon.rank
                parent_taxon.status = record_parent_taxon.status
                if record_parent_taxon.valid_name:
                    parent_taxon.is_valid = True
                synonyms = Aphia().get_aphia_synonyms_by_id(record_parent_taxon.AphiaID)
                for synonym in synonyms:
                    if synonym.status == 'accepted':
                        syn, created_syn = Taxon.objects.get_or_create(name=synonym.scientificname)
                        if created_syn:
                            syn.aphia = synonym.AphiaID
                            syn.authority = synonym.authority
                            if synonym.rank in self._RANKS_NAMES.keys():
                                syn.rank = self._RANKS_NAMES[synonym.rank]
                            else:
                                syn.rank = synonym.rank
                            syn.status = synonym.status
                            if synonym.valid_name:
                                syn.is_valid = True
                            syn.valid_taxon = parent_taxon
                parent_taxon.valid_taxon = parent_taxon
                if parent_name != 'Biota':
                    granpa_taxon = Taxon.objects.get(name=self._update_parents_taxon(parent_name))
                    parent_taxon.parent = granpa_taxon
                parent_taxon.save()
        return parent_name
                

"""parent_name = Aphia().get_aphia_name_by_id(parent_id)
if parent_name == 'Biota':
t, created = Taxon.objects.get_or_create(name=parent_name)
if created:
    aphia = Aphia().get_aphia_id(taxon_name)
    record = Aphia().get_aphia_record_by_id(aphia)
    t.rank = record.rank
    t.authority = record.authority
else:"""

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class CoauthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('name', 'id')
        