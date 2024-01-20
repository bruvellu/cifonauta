from rest_framework import serializers
from .models import Reference

class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reference
        fields = '__all__'

    def validate_name(self, value):
        reference = Reference.objects.filter(name=value)
        if reference.exists():
            raise serializers.ValidationError(f'DOI já existe no banco de dados')
        return value