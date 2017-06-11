# -*- coding: utf-8 -*-
from django.test import TestCase

from tandlr.catalogues.models import University


class UniversityTest(TestCase):

    def setUp(self):

        self.university = University.objects.create(
            name='New University'
        )

    def test_name(self):

        self.assertEqual(self.university.__unicode__(), 'New University')
