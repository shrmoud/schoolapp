# -*- coding: utf-8 -*-
import json

from django.core.urlresolvers import reverse

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

from tandlr.catalogues.models import University


class ApiTests(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.client.post(
            reverse('api:v1:register-list'),
            {
                'username': 'test',
                'email': 'test@test.com',
                'password': 'test_password',
                'device_os': 'IOS',
                'gender': 2,
            },
            format='json'
        )

        #
        # Login the user to the platform before running every test
        #
        self.login_response = self.client.post(
            reverse('api:v1:login-list'),
            {
                'email': 'test@test.com',
                'password': 'test_password',
                'device_os': 'IOS'
            },
            format='json'
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=('JWT ' + self.login_response.data.get('token'))
        )

        self.university = University.objects.create(
            name="New University",
            initial="NU",
        )

        self.another_university = University.objects.create(
            name="Another University",
            initial="AU",
        )

    def test_get_university(self):
        url = reverse('api:v2:universities-list')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detail_university(self):
        url = reverse(
            'api:v2:universities-detail',
            kwargs={
                'pk': str(self.university.id)
            }
        )

        response = self.client.get(
            url,
            format='json'
        )

        self.assertEqual(response.data['id'], self.university.id)

    def test_filter_university(self):
        url = '/api/v2/catalogues/universities?q=new'

        response = self.client.get(
            url,
            format='json'
        )

        result = json.loads(response.content)
        q = result['results'][0]['name']
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(q, 'New University')
