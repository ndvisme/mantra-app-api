
from http import client
from unicodedata import name
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Mantra,
    Tag,
)

from mantra.serializers import (
    MantraSerializer,
    MantraDetailSerializer,
)


MANTRA_URL = reverse('mantra:mantra-list')


def detail_url(mantra_id):
    return reverse('mantra:mantra-detail', args=[mantra_id])


def create_mantra(user, **params):
    defaults = {
        'quote': 'I surrender to the flow and have faith in the ultimate good.',
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

    def test_create_mantra_with_new_tags(self):
        payload = {
            'quote': 'I surrender to the flow and have faith in the ultimate good.',
            'public': False,
            'tags': [{'name': 'Spirit'}, {'name': 'Soul'}]
        }
        res = self.client.post(MANTRA_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mantras = Mantra.objects.filter(user=self.user)
        self.assertEqual(mantras.count(), 1)
        mantra = mantras[0]
        self.assertEqual(mantra.tags.count(), 2)
        for tag in payload['tags']:
            exists = mantra.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_mantra_wtih_existing_tags(self):
        tag_soul = Tag.objects.create(user=self.user, name='Soul')
        payload = {
            'quote': 'I surrender to the flow and have faith in the ultimate good.',
            'public': False,
            'tags': [{'name': 'Soul'}, {'name': 'Inner Peace'}]
        }
        res = self.client.post(MANTRA_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        mantras = Mantra.objects.filter(user=self.user)
        self.assertEqual(mantras.count(), 1)
        mantra = mantras[0]
        self.assertEqual(mantra.tags.count(), 2)
        self.assertIn(tag_soul, mantra.tags.all())
        for tag in payload['tags']:
            exists = mantra.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        mantra = create_mantra(user=self.user)

        payload = {'tags': [{'name': 'Inner Peace'}]}
        url = detail_url(mantra.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Inner Peace')
        self.assertIn(new_tag, mantra.tags.all())

    def test_update_mantra_assign_tag(self):
        tag_body = Tag.objects.create(user=self.user, name='Body')
        mantra = create_mantra(user=self.user)
        mantra.tags.add(tag_body)

        tag_love_the_world = Tag.objects.create(user=self.user, name='Love the World')
        payload = {'tags': [{'name': 'Love the World'}]}
        url = detail_url(mantra.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_love_the_world, mantra.tags.all())
        self.assertNotIn(tag_body, mantra.tags.all())

    def test_clear_recipe_tags(self):
        tag = Tag.objects.create(user=self.user, name='Soul')
        mantra = create_mantra(self.user)
        mantra.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(mantra.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(mantra.tags.count(), 0)






