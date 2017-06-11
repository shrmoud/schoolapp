# -*- coding: utf-8 -*-

import json
from datetime import time

from django.contrib.auth import get_user_model
from django.test import TestCase

from tandlr.scheduled_classes.models import Class, ClassStatus, Subject
from tandlr.stripe.models import StripeCard, StripeCharge, StripeCustomer
from tandlr.stripe.tests.mocks import MockCard, MockCharge, MockCustomer


class StripeCardTest(TestCase):

    def setUp(self):
        self.mock_card = json.loads(MockCard().getCard())
        self.mock_customer = json.loads(MockCustomer().getCustomer())

        self.user = get_user_model().objects.last()

        self.customer = StripeCustomer.objects.create(
            user=self.user,
            account_balance=self.mock_customer.get('account_balance'),
            delinquent=self.mock_customer.get('delinquent'),
            default_source=self.mock_customer.get('default_source'),
            customer_id=self.mock_customer.get('id')
        )

        self.card = StripeCard.objects.create(
            card_id=self.mock_card.get('id'),
            customer=self.customer,
            name=self.mock_card.get('name'),
            address_line_1=self.mock_card.get('address_line1'),
            address_line_1_check=self.mock_card.get('address_line1_check'),
            address_line_2=self.mock_card.get('address_line2'),
            address_city=self.mock_card.get('address_city'),
            address_state=self.mock_card.get('address_state'),
            address_country=self.mock_card.get('address_country'),
            address_zip=self.mock_card.get('address_zip'),
            address_zip_check=self.mock_card.get('address_zip_check'),
            brand=self.mock_card.get('brand'),
            country=self.mock_card.get('country'),
            cvc_check=self.mock_card.get('cvc_check'),
            dynamic_last4=self.mock_card.get('dynamic_last4'),
            tokenization_method=self.mock_card.get('tokenization_method'),
            exp_month=self.mock_card.get('exp_month'),
            exp_year=self.mock_card.get('exp_year'),
            funding=self.mock_card.get('funding'),
            last4=self.mock_card.get('last4'),
            fingerprint=self.mock_card.get('fingerprint')
        )

    def tearDown(self):

        self.card.delete()
        self.customer.delete()

    def test_the_object_is_created_correctly_inside_the_database(self):

        card_to_test = StripeCard.objects.get(card_id=self.card.card_id)

        self.assertEqual(card_to_test.id, self.card.id)

        self.assertEqual(card_to_test.card_id, self.card.card_id)

        self.assertEqual(card_to_test.customer, self.customer)

        self.assertEqual(card_to_test.address_line_1, self.card.address_line_1)

        self.assertEqual(
            card_to_test.address_line_1_check,
            self.card.address_line_1_check
        )

        self.assertEqual(card_to_test.address_line_2, self.card.address_line_2)

        self.assertEqual(card_to_test.address_city, self.card.address_city)

        self.assertEqual(card_to_test.address_state, self.card.address_state)

        self.assertEqual(
            card_to_test.address_country,
            self.card.address_country
        )
        self.assertEqual(card_to_test.address_zip, self.card.address_zip)

        self.assertEqual(
            card_to_test.address_zip_check,
            self.card.address_zip_check
        )

        self.assertEqual(
            card_to_test.brand,
            self.card.brand
        )

        self.assertEqual(
            card_to_test.country,
            self.card.country
        )

        self.assertEqual(
            card_to_test.cvc_check,
            self.card.cvc_check
        )

        self.assertEqual(
            card_to_test.dynamic_last4,
            self.card.dynamic_last4
        )

        self.assertEqual(
            card_to_test.tokenization_method,
            self.card.tokenization_method
        )

        self.assertEqual(
            card_to_test.exp_month,
            self.card.exp_month
        )

        self.assertEqual(
            card_to_test.exp_year,
            self.card.exp_year
        )

        self.assertEqual(
            card_to_test.funding,
            self.card.funding
        )

        self.assertEqual(
            card_to_test.last4,
            self.card.last4
        )

        self.assertEqual(
            card_to_test.fingerprint,
            self.card.fingerprint
        )


class StripeChargeTest(TestCase):

    def setUp(self):
        self.mock_card = json.loads(MockCard().getCard())
        self.mock_customer = json.loads(MockCustomer().getCustomer())
        self.mock_charge = json.loads(MockCharge().getCharge())

        self.user = get_user_model().objects.create(
            username='test',
            password='1',
            email='q@q.com'
        )

        self.class_status = ClassStatus.objects.create(
            name="status",
            description="status"
        )

        self.class_subject = Subject.objects.create(
            name="subject",
            description="subject",
            price_per_hour=9.99
        )

        self.related_class = Class.objects.create(
            class_start_date="2016-07-14 20:00:52.921276+00:00",
            teacher=self.user,
            student=self.user,
            subject=self.class_subject,
            class_status=self.class_status,
            class_time=time(hour=1, minute=0),
            class_detail="testing class",
            participants=1,
            time_zone_conf=5,
            location=(
                u"SRID=4326;POINT "
                u"(19.4619810000000015 -99.1511504000000059)"
            )
        )

        self.customer = StripeCustomer.objects.create(
            user=self.user,
            account_balance=self.mock_customer.get('account_balance'),
            delinquent=self.mock_customer.get('delinquent'),
            default_source=self.mock_customer.get('default_source'),
            customer_id=self.mock_customer.get('id')
        )

        self.card = StripeCard.objects.create(
            card_id=self.mock_card.get('id'),
            customer=self.customer,
            name=self.mock_card.get('name'),
            address_line_1=self.mock_card.get('address_line1'),
            address_line_1_check=self.mock_card.get('address_line1_check'),
            address_line_2=self.mock_card.get('address_line2'),
            address_city=self.mock_card.get('address_city'),
            address_state=self.mock_card.get('address_state'),
            address_country=self.mock_card.get('address_country'),
            address_zip=self.mock_card.get('address_zip'),
            address_zip_check=self.mock_card.get('address_zip_check'),
            brand=self.mock_card.get('brand'),
            country=self.mock_card.get('country'),
            cvc_check=self.mock_card.get('cvc_check'),
            dynamic_last4=self.mock_card.get('dynamic_last4'),
            tokenization_method=self.mock_card.get('tokenization_method'),
            exp_month=self.mock_card.get('exp_month'),
            exp_year=self.mock_card.get('exp_year'),
            funding=self.mock_card.get('funding'),
            last4=self.mock_card.get('last4'),
            fingerprint=self.mock_card.get('fingerprint')
        )

        self.charge = StripeCharge.objects.create(
            charge_id=self.mock_charge.get('id'),
            customer=self.customer,
            card=self.card,
            amount=self.mock_charge.get('amount'),
            amount_refunded=self.mock_charge.get('amount_refunded'),
            description=self.mock_charge.get('description'),
            paid=self.mock_charge.get('paid'),
            disputed=self.mock_charge.get('disputed'),
            refunded=self.mock_charge.get('refunded'),
            captured=self.mock_charge.get('captured'),
            charge_created=self.mock_charge.get('charge_created'),
            related_class=self.related_class
        )

    def tearDown(self):

        self.class_status.delete()
        self.class_subject.delete()
        self.related_class.delete()
        self.charge.delete()
        self.card.delete()
        self.customer.delete()
        self.user.delete()

    def test_the_object_is_created_correctly_inside_the_database(self):

        charge_to_test = StripeCharge.objects.get(
            charge_id=self.charge.charge_id
        )

        self.assertEqual(charge_to_test.id, self.charge.id)

        self.assertEqual(charge_to_test.customer, self.customer)

        self.assertEqual(charge_to_test.card, self.card)

        self.assertEqual(charge_to_test.currency, self.charge.currency)

        self.assertEqual(charge_to_test.amount, self.charge.amount)

        self.assertEqual(
            charge_to_test.amount_refunded,
            self.charge.amount_refunded
        )

        self.assertEqual(
            charge_to_test.description,
            self.charge.description
        )

        self.assertEqual(
            charge_to_test.paid,
            self.charge.paid
        )

        self.assertEqual(
            charge_to_test.disputed,
            self.charge.disputed
        )

        self.assertEqual(
            charge_to_test.refunded,
            self.charge.refunded
        )

        self.assertEqual(
            charge_to_test.captured,
            self.charge.captured
        )

        self.assertEqual(
            charge_to_test.charge_created,
            self.charge.charge_created
        )

        self.assertEqual(
            charge_to_test.related_class,
            self.related_class
        )


class StripeCustomerTest(TestCase):

    def setUp(self):
        self.mock_customer = json.loads(MockCustomer().getCustomer())

        self.user = get_user_model().objects.last()

        self.customer = StripeCustomer.objects.create(
            user=self.user,
            account_balance=self.mock_customer.get('account_balance'),
            delinquent=self.mock_customer.get('delinquent'),
            default_source=self.mock_customer.get('default_source'),
            customer_id=self.mock_customer.get('id')
        )

    def tearDown(self):

        self.customer.delete()

    def test_the_object_is_created_correctly_inside_the_database(self):

            customer_to_test = StripeCustomer.objects.get(
                customer_id=self.customer.customer_id
            )

            self.assertEqual(
                customer_to_test.id,
                self.customer.id
            )

            self.assertEqual(
                customer_to_test.user,
                self.user
            )

            self.assertEqual(
                customer_to_test.account_balance,
                self.customer.account_balance
            )

            self.assertEqual(
                customer_to_test.currency,
                self.customer.currency
            )

            self.assertEqual(
                customer_to_test.delinquent,
                self.customer.delinquent
            )

            self.assertEqual(
                customer_to_test.default_source,
                self.customer.default_source
            )
