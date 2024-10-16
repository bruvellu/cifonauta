from rest_framework import serializers

from .models import Reference, Taxon, Location, Person


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = '__all__'

    def validate_doi(self, value):
        reference = Reference.objects.filter(doi=value)
        if reference.exists():
            raise serializers.ValidationError(f'DOI já existe no banco de dados')
        return value

class TaxonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxon
        fields = '__all__'
        
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class CoauthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ('name', 'id')

