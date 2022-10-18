
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Mantra

from mantra.serializers import (
    MantraSerializer,
    MantraDetailSerializer,
)


MANTRA_URL = reverse('mantra:mantra-list')


def detail_url(mantra_id):
    return reverse('mantra:mantra-detail', args=[mantra_id])


def create_mantra(user, **params):
    defaults = {
        'quote': 'All we have to decide is what to do with the time that is given to us',
        'public': False,
    }
    defaults.update(params)

    mantra = Mantra.objects.create(user=user, **defaults)
    return mantra

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicMantraAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(MANTRA_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateMantraAPITests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_retrive_recipes(self):
        create_mantra(user=self.user)
        create_mantra(user=self.user)

        res = self.client.get(MANTRA_URL)

        mantras = Mantra.objects.all().order_by('-id')
        serializer = MantraSerializer(mantras, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_mantra_list_limited_to_user(self):
        other_user = create_user(email='other@example.com', password='test123')
        create_mantra(user=other_user)
        create_mantra(user=self.user)

        res = self.client.get(MANTRA_URL)

        mantras = Mantra.objects.filter(user=self.user)
        serializer = MantraSerializer(mantras, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_mantra_detail(self):
        mantra = create_mantra(user=self.user)

        url = detail_url(mantra.id)
        res = self.client.get(url)

        serializer = MantraDetailSerializer(mantra)
        self.assertEqual(res.data, serializer.data)

    def test_create_mantra(self):
        payload = {
            'quote': 'All we have to decide is what to do with the time that is given to us',
            'public': False,
        }
        res = self.client.post(MANTRA_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mantra = Mantra.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(mantra, k), v)
        self.assertEqual(mantra.user, self.user)


