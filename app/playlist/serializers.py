
from rest_framework import serializers

from core.models import (
    Playlist,
    Mantra,
)

from mantra.serializers import MantraSerializer


class PlaylistSerializer(serializers.ModelSerializer):

    mantras = MantraSerializer(many=True, required=False)

    class Meta:
        model = Playlist
        fields = ['id', 'title', 'mantras']
        read_only_fields = ['id']

    def _get_or_create_mantras(self, mantras, playlist):
        auth_user = self.context['request'].user
        for mantra in mantras:
            mantra_obj, created = Mantra.objects.get_or_create(
                user=auth_user,
                **mantra,
            )
            playlist.mantras.add(mantra_obj)

    def create(self, validated_data):
        mantras = validated_data.pop('mantras', [])
        playlist = Playlist.objects.create(**validated_data)
        self._get_or_create_mantras(mantras, playlist)

        return playlist

    def update(self, instance, validated_data):
        mantras = validated_data.pop('mantras', None)
        if mantras is not None:
            instance.mantras.clear()
            self._get_or_create_mantras(mantras, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class PlaylistDetailSerializer(PlaylistSerializer):

    class Meta(PlaylistSerializer.Meta):
        fields = PlaylistSerializer.Meta.fields + ['description', 'public']