# -*- coding: utf-8 -*-
import json

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

from tandlr.users.models import DeviceUser


class AuthViewsTestCase(TestCase):
    """
    Tests for the views and forms of the tandlr.authentication module.
    """
    def setUp(self):
        self.login_url = reverse('api:v1:login-list')
        self.logout_url = reverse('api:v1:logout-list')

        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='user',
            email='user@example.com',
            password='secret'
        )

    def test_get_login_view_returns_405(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 405)

    def test_login_succeeds_with_correct_credentials(self):
        response = self.client.post(
            self.login_url,
            json.dumps({
                'email': 'user@example.com',
                'password': 'secret',
                'device_os': 'mobile'
            }),
            'application/json'
        )

        self.assertEqual(response.status_code, 200)

    def test_login_fails_with_incorrect_credentials(self):
        response = self.client.post(
            self.login_url,
            json.dumps({
                'email': 'user@example.com',
                'password': 'not-the-secret',
                'device_os': 'mobile'
            }),
            'application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {
            'non_field_errors': ['invalid credentials']
        })

        response = self.client.post(
            self.login_url,
            json.dumps({
                'email': 'non-existing-user@example.com',
                'password': 'some-password',
                'device_os': 'mobile'
            }),
            'application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {
            'non_field_errors': ['invalid credentials']
        })

    def test_login_creates_active_user_device(self):
        self.assertEqual(DeviceUser.objects.count(), 0)

        self.client.post(
            self.login_url,
            json.dumps({
                'email': 'user@example.com',
                'password': 'secret',
                'device_os': 'mobile',
                'device_user_token': 'abc123'
            }),
            'application/json'
        )

        self.assertEqual(DeviceUser.objects.count(), 1)

        device = DeviceUser.objects.last()
        self.assertTrue(device.is_active)
        self.assertEqual(device.user, self.user)
        self.assertEqual(device.device_os, 'mobile')
        self.assertEqual(device.device_user_token, 'abc123')

    def test_logout_disables_user_device(self):
        response = self.client.post(
            self.login_url,
            json.dumps({
                'email': 'user@example.com',
                'password': 'secret',
                'device_os': 'mobile',
                'device_user_token': 'abc123'
            }),
            'application/json'
        )

        data = json.loads(response.content)

        response = self.client.post(
            self.logout_url,
            json.dumps({
                'device_os': 'mobile',
                'device_user_token': 'abc123'
            }),
            'application/json',
            HTTP_AUTHORIZATION='jwt {0}'.format(data['token'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'is_active': False,
            'device_os': 'mobile',
            'device_user_token': 'abc123'
        })

        device = DeviceUser.objects.last()
        self.assertFalse(device.is_active)

    def test_logout_with_incorrect_device_returns_error(self):
        response = self.client.post(
            self.login_url,
            json.dumps({
                'email': 'user@example.com',
                'password': 'secret',
                'device_os': 'mobile',
                'device_user_token': 'abc123'
            }),
            'application/json'
        )

        data = json.loads(response.content)

        response = self.client.post(
            self.logout_url,
            json.dumps({
                'device_os': 'mobile',
                'device_user_token': 'bad-token'
            }),
            'application/json',
            HTTP_AUTHORIZATION='jwt {0}'.format(data['token'])
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {
            'non_field_errors': ['invalid device']
        })

        response = self.client.post(
            self.logout_url,
            json.dumps({
                'device_os': 'bad-os',
                'device_user_token': 'abc123'
            }),
            'application/json',
            HTTP_AUTHORIZATION='jwt {0}'.format(data['token'])
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {
            'non_field_errors': ['invalid device']
        })

    def test_logout_without_device_user_token_succeeds(self):
        response = self.client.post(
            self.login_url,
            json.dumps({
                'email': 'user@example.com',
                'password': 'secret',
                'device_os': 'mobile'
            }),
            'application/json'
        )

        data = json.loads(response.content)

        response = self.client.post(
            self.logout_url,
            json.dumps({
                'device_os': 'mobile'
            }),
            'application/json',
            HTTP_AUTHORIZATION='jwt {0}'.format(data['token'])
        )

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {
            'is_active': False,
            'device_os': 'mobile',
            'device_user_token': None
        })

        device = DeviceUser.objects.last()
        self.assertFalse(device.is_active)
