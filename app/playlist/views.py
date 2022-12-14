
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

from core.models import Playlist
from playlist import serializers


class PlaylistViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PlaylistDetailSerializer
    queryset = Playlist.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PlaylistSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def public(self, request, pk=None):
        playlists = self.queryset.filter(public=True).order_by('-id')
        serializer = self.serializer_class(playlists, many=True)
        return Response(serializer.data)




