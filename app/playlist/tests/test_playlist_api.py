
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Playlist

from playlist.serializers import (
    PlaylistSerializer,
    PlaylistDetailSerializer,
)


PLAYLIST_URL = reverse('playlist:playlist-list')


def detail_url(playlist_id):
    return reverse('playlist:playlist-detail', args=[playlist_id])


def create_playlist(user, **params):
    defaults = {
        'title': 'Sample playlist title',
        'description': 'Sample description',
        'public': False,
    }
    defaults.update(params)

    playlist = Playlist.objects.create(user=user, **defaults)
    return playlist

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicPlaylistAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLAYLIST_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePlaylistTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(
            email='user@example.com',
            password='test123',
            )
        self.client.force_authenticate(self.user)

    def test_retrive_playlists(self):
        create_playlist(user=self.user)
        create_playlist(user=self.user)

        res = self.client.get(PLAYLIST_URL)

        playlists = Playlist.objects.all().order_by('-id')
        serializer = PlaylistSerializer(playlists, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_playlist_list_limited_to_user(self):
        other_user = create_user(
            email='otheruser@example.com',
            password='test123',
            )
        create_playlist(user=other_user)
        create_playlist(user=self.user)

        res = self.client.get(PLAYLIST_URL)

        playlists = Playlist.objects.filter(user=self.user)
        serializer = PlaylistSerializer(playlists, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_playlist_detail(self):
        playlist = create_playlist(user=self.user)

        url = detail_url(playlist.id)
        res = self.client.get(url)

        serializer = PlaylistDetailSerializer(playlist)
        self.assertEqual(res.data, serializer.data)

    def test_create_playlist(self):
        payload = {
            'title': 'Sample playlist',
            'description': 'Sample description',
            'public': False,
        }
        res = self.client.post(PLAYLIST_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        playlist = Playlist.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(playlist, k), v)
        self.assertEqual(playlist.user, self.user)








