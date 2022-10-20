
from rest_framework import serializers

from core.models import Playlist


class PlaylistSerializer(serializers.ModelSerializer):

    class Meta:
        model = Playlist
        fields = ['id', 'title']
        read_only_fields = ['id']


class PlaylistDetailSerializer(PlaylistSerializer):

    class Meta(PlaylistSerializer.Meta):
        fields = PlaylistSerializer.Meta.fields + ['description', 'public']