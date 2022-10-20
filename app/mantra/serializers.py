
from rest_framework import serializers

from core.models import (
    Mantra,
    Tag,
)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class MantraSerializer(serializers.ModelSerializer):

    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Mantra
        fields = ['id', 'quote', 'tags']
        read_only_fields = ['id']

    def _get_or_create_tags(self, tags, mantra):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            mantra.tags.add(tag_obj)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        mantra = Mantra.objects.create(**validated_data)
        self._get_or_create_tags(tags, mantra)

        return mantra

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class MantraDetailSerializer(MantraSerializer):

    class Meta(MantraSerializer.Meta):
        fields = MantraSerializer.Meta.fields + ['public']
