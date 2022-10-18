
from rest_framework import serializers

from core.models import Mantra


class MantraSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mantra
        fields = ['id', 'quote']
        read_only_fields = ['id']


class MantraDetailSerializer(MantraSerializer):

    class Meta(MantraSerializer.Meta):
        fields = MantraSerializer.Meta.fields + ['public']

