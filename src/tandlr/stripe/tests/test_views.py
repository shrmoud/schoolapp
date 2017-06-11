# -*- coding: utf-8 -*-
import json

from datetime import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import TestCase

import httpretty

from rest_framework.test import APIClient

import stripe

from tandlr.scheduled_classes.models import (
    Class,
    ClassStatus,
    RequestClassExtensionTime,
    Subject,
    SubjectTeacher
)
from tandlr.stripe.models import StripeCard, StripeCustomer
from tandlr.stripe.utils import generate_charge_description


class MakeANewChargeInStripe(TestCase):

    def setUp(self):

        self.maxDiff = None
        expected_json = {
            "customer_id": "cus_842ErI0D7xCGm1",
            "cards": [
                {
                    "card_id": "card_17nu9mJNKLANSXXXNZlzhQge",
                    "last4": "4444",
                    "brand": "MasterCard",
                    "name": u"Javier Castañeda",
                    "customer": {
                        "customer_id": "cus_842ErI0D7xCGm1",
                        "user": {
                            "id": 2,
                            "username": "cus_842ErI0D7xCGm1",
                            "name": None,
                            "last_name": None,
                            "second_last_name": None,
                            "description": None,
                            "email": "q@q.com"
                        }
                    }
                }
            ]
        }

        self.expected_json = json.dumps(expected_json)

        stripe.api_key = settings.STRIPE_PRIVATE_KEY

        self.client = APIClient()

        self.client.post(
            reverse('api:v2:registration-list'),
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
            reverse('api:v2:auth-login'),
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

        self.stripe_cards = []
        self.stripe_customer = None

        self.class_status = None
        self.class_status_2 = None
        self.class_status_3 = None

        self.related_class = None
        self.class_extension = None

        self.another_class = None

        self.class_subject = None

        self.teacher_subject = None

        self.user = None
        self.another_user = None

    @httpretty.activate
    def create_customer_and_card(self, customer_id):
        custumer_data = {
            "id": "{}".format(customer_id),
            "object": "customer",
            "account_balance": 0,
            "business_vat_id": None,
            "created": 1461863006,
            "currency": None,
            "default_source": "card_17nu9mJNKLANSXXXNZlzhQge",
            "delinquent": False,
            "description": "Javier Castañeda",
            "discount": None,
            "email": "q@q.com",
            "livemode": False,
            "metadata": {},
            "shipping": None,
            "sources": {
                "object": "list",
                "data": [
                    {
                        "id": "card_17nu9mJNKLANSXXXNZlzhQge",
                        "object": "card",
                        "address_city": None,
                        "address_country": None,
                        "address_line1": None,
                        "address_line1_check": None,
                        "address_line2": None,
                        "address_state": None,
                        "address_zip": None,
                        "address_zip_check": None,
                        "brand": "MasterCard",
                        "country": "US",
                        "customer": "cus_8M0Z2V20QoOpMS",
                        "cvc_check": "pass",
                        "dynamic_last4": None,
                        "exp_month": 12,
                        "exp_year": 2017,
                        "fingerprint": "Xt5EWLLDS7FJjR1c",
                        "funding": "credit",
                        "last4": "4444",
                        "metadata": {},
                        "name": "Javier Castañeda",
                        "tokenization_method": None
                    }
                ],
                "has_more": False,
                "total_count": 1,
                "url": "/v1/customers/cus_8M0Z2V20QoOpMS/sources"
            },
            "subscriptions": {
                "object": "list",
                "data": [],
                "has_more": False,
                "total_count": 0,
                "url": "/v1/customers/cus_8M0Z2V20QoOpMS/subscriptions"
            }
        }
        httpretty.register_uri(
            httpretty.GET,
            "https://api.stripe.com/v1/customers/{}".format(customer_id),
            body=json.dumps(custumer_data),
            status=200
        )

        #
        # Customer created for the testing of Charges and cards
        #
        self.customer = stripe.Customer.retrieve(customer_id)

        #
        # Cards created for the testing of Charges and cards
        #
        self.cards = self.customer.sources.data

        self.user = get_user_model().objects.create(
            username=customer_id,
            password='1',
            email='q@q.com',
            is_teacher=True
        )

        self.another_user = get_user_model().objects.create(
            username='anotherUser',
            password='1',
            email='a@a.com'
        )

        #
        # Create the stripeCustomer inside the database for testing
        #
        self.stripe_customer = StripeCustomer.objects.create(
            user=self.user,
            account_balance=self.customer.account_balance,
            delinquent=self.customer.delinquent,
            default_source=self.customer.default_source,
            customer_id=self.customer.id
        )

        self.stripe_cards = []
        for card in self.cards:
            self.stripe_cards.append(
                StripeCard.objects.create(
                    customer=self.stripe_customer,
                    name=card.name,
                    address_line_1=card.address_line1,
                    address_line_1_check=card.address_line1_check,
                    address_line_2=card.address_line2,
                    address_city=card.address_city,
                    address_state=card.address_state,
                    address_country=card.address_country,
                    address_zip=card.address_zip,
                    address_zip_check=card.address_zip_check,
                    brand=card.brand,
                    country=card.country,
                    cvc_check=card.cvc_check,
                    dynamic_last4=card.dynamic_last4,
                    tokenization_method=card.tokenization_method,
                    exp_month=card.exp_month,
                    exp_year=card.exp_year,
                    funding=card.funding,
                    last4=card.last4,
                    fingerprint=card.fingerprint,
                    card_id=card.id
                )
            )

            self.class_status = ClassStatus.objects.create(
                name="status",
                description="status"
            )

            self.class_status_2 = ClassStatus.objects.create(
                name="status2",
                description="status2"
            )

            self.class_status_3 = ClassStatus.objects.create(
                name="acecpted",
                description="acecpted"
            )

            self.class_subject = Subject.objects.create(
                name="subject",
                description="subject",
                price_per_hour=9.99
            )

            self.teacher_subject = SubjectTeacher.objects.create(
                teacher=self.user,
                subject=self.class_subject,
                status=True
            )

            self.related_class = Class.objects.create(
                class_start_date="2016-07-14 20:00:52.921276+00:00",
                teacher=self.user,
                student=self.user,
                subject=self.class_subject,
                class_status=self.class_status,
                class_detail="testing class",
                participants=1,
                class_time=time(hour=1, minute=0),
                time_zone_conf=5,
                location=(
                    u"SRID=4326;POINT "
                    u"(19.4619810000000015 -99.1511504000000059)"
                )
            )

            self.class_extension_1 = RequestClassExtensionTime.objects.create(
                class_request=self.related_class,
                time=time(0, 30, 0, 0)
            )

            self.another_class = Class.objects.create(
                class_start_date="2016-07-14 20:00:52.921276+00:00",
                teacher=self.another_user,
                student=self.another_user,
                subject=self.class_subject,
                class_status=self.class_status_2,
                class_time=time(hour=1, minute=0),
                class_detail="testing class",
                participants=2,
                time_zone_conf=5,
                location=(
                    u"SRID=4326;POINT "
                    u"(19.4619810000000015 -99.1511504000000059)"
                )
            )

            self.class_extension_2 = RequestClassExtensionTime.objects.create(
                class_request=self.another_class,
                time=time(0, 30, 0, 0)
            )

    def tearDown(self):

        if self.class_status:
            self.class_status.delete()

        if self.class_subject:
            self.class_subject.delete()

        if self.related_class:
            self.related_class.delete()

        if self.another_class:
            self.another_class.delete()

        if self.stripe_cards:
            for card in self.stripe_cards:
                card.delete()

        if self.stripe_customer:
            self.stripe_customer.delete()

    @httpretty.activate
    def test_the_user_should_be_able_to_create_a_new_charge(self):
        charges_data = {
            "id": "ch_185IYD2eZvKYlo2CiprQHol4",
            "object": "charge",
            "amount": 2000,
            "amount_refunded": 0,
            "application_fee": None,
            "balance_transaction": "txn_185IYD2eZvKYlo2CeR0Oax5g",
            "captured": True,
            "created": 1461863021,
            "currency": "usd",
            "customer": "cus_842ErI0D7xCGm1",
            "description": None,
            "destination": None,
            "dispute": None,
            "failure_code": None,
            "failure_message": None,
            "fraud_details": {},
            "invoice": None,
            "livemode": False,
            "metadata": {},
            "order": None,
            "paid": True,
            "receipt_email": None,
            "receipt_number": None,
            "refunded": False,
            "refunds": {
                "object": "list",
                "data": [],
                "has_more": False,
                "total_count": 0,
                "url": "/v1/charges/ch_185IYD2eZvKYlo2CiprQHol4/refunds"
            },
            "shipping": None,
            "source": {
                "id": "card_17nu9mJNKLANSXXXNZlzhQge",
                "object": "card",
                "address_city": None,
                "address_country": None,
                "address_line1": None,
                "address_line1_check": None,
                "address_line2": None,
                "address_state": None,
                "address_zip": None,
                "address_zip_check": None,
                "brand": "Visa",
                "country": "US",
                "customer": "cus_842ErI0D7xCGm1",
                "cvc_check": "pass",
                "dynamic_last4": None,
                "exp_month": 12,
                "exp_year": 2017,
                "fingerprint": "Xt5EWLLDS7FJjR1c",
                "funding": "credit",
                "last4": "4242",
                "metadata": {},
                "name": "Javier Castañeda",
                "tokenization_method": None
            },
            "source_transfer": None,
            "statement_descriptor": None,
            "status": "succeeded"
        }

        httpretty.register_uri(
            httpretty.POST, "https://api.stripe.com/v1/charges",
            body=json.dumps(charges_data),
            status=201
        )

        self.create_customer_and_card('cus_842ErI0D7xCGm1')

        #
        # Create a new charge for the user
        #
        response = self.client.post(
            reverse('api:v1:stripe-charges-list'),
            {
                'currency': 'usd',
                'customer_id': self.customer.id,
                'description': 'testing charge',
                'class_id': self.related_class.id
            },
            format='json'
        )

        #
        # If everything was correct the answer should be a 201 http response
        # with a success message and a charge id. If the charge was created in
        # Stripe then is possible to retrieve it
        #
        self.assertEqual(response.status_code, 201)

        # Testing information returned from the serializer.
        self.assertEqual(response.data.get('amount'), "9.99")

        # Checking related class information.
        data = response.data
        self.assertEqual(data['related_class']['id'], 1)
        self.assertEqual(data['related_class']['teacher'], 2)
        self.assertEqual(data['related_class']['student'], 2)
        self.assertEqual(data['related_class']['subject']['id'], 1)

        # Testing the spected information against the stripe charge
        # information.
        created_charge = stripe.Charge.retrieve(response.data.get('charge_id'))

        self.assertEqual(created_charge.amount, 999)
        self.assertEqual(created_charge.currency, 'usd')
        self.assertEqual(created_charge.description, 'testing charge')
        self.assertEqual(created_charge.amount_refunded, 0)

    def test_customer_detail_information_by_user_id(self):

        self.create_customer_and_card('cus_842ErI0D7xCGm1')

        #
        # Getting the customer information.
        #
        response = self.client.get(
            reverse('api:v1:stripe-customers-detail', kwargs={'pk': 2}),
            format='json'
        )

        self.assertJSONEqual(response.content, self.expected_json)

    def test_customer_detail_information_by_customer_id(self):

        self.create_customer_and_card('cus_842ErI0D7xCGm1')

        #
        # Getting the customer information.
        #
        response = self.client.get(
            reverse(
                'api:v1:stripe-customers-detail',
                kwargs={
                    'pk': self.customer.id
                }
            ),
            format='json'
        )

        self.assertJSONEqual(response.content, self.expected_json)

    @httpretty.activate
    def test_address_line1_is_incorrect_for_the_card(self):
        """
        This test is designed for the card with number 4000 0000 0000 0010
        where the address_line1 and address_zip are incorrect to check that
        the error message is managed correctly. All the customers where
        created with the console, if there is a problem with the customer
        a new token should be generated, a new customer created and the
        customer_id should be replaced.
        """
        charges_data = {
            "id": "ch_185IYD2eZvKYlo2CiprQHol4",
            "object": "charge",
            "amount": 2000,
            "amount_refunded": 0,
            "application_fee": None,
            "balance_transaction": "txn_185IYD2eZvKYlo2CeR0Oax5g",
            "captured": True,
            "created": 1461863021,
            "currency": "usd",
            "customer": "cus_842ErI0D7xCGm1",
            "description": None,
            "destination": None,
            "dispute": None,
            "failure_code": None,
            "failure_message": None,
            "fraud_details": {},
            "invoice": None,
            "livemode": False,
            "metadata": {},
            "order": None,
            "paid": True,
            "receipt_email": None,
            "receipt_number": None,
            "refunded": False,
            "refunds": {
                "object": "list",
                "data": [],
                "has_more": False,
                "total_count": 0,
                "url": "/v1/charges/ch_185IYD2eZvKYlo2CiprQHol4/refunds"
            },
            "shipping": None,
            "source": {
                "id": "card_17nu9mJNKLANSXXXNZlzhQge",
                "object": "card",
                "address_city": None,
                "address_country": None,
                "address_line1": None,
                "address_line1_check": None,
                "address_line2": None,
                "address_state": None,
                "address_zip": None,
                "address_zip_check": None,
                "brand": "Visa",
                "country": "US",
                "customer": "cus_842ErI0D7xCGm1",
                "cvc_check": "pass",
                "dynamic_last4": None,
                "exp_month": 12,
                "exp_year": 2017,
                "fingerprint": "Xt5EWLLDS7FJjR1c",
                "funding": "credit",
                "last4": "4242",
                "metadata": {},
                "name": "Javier Castañeda",
                "tokenization_method": None
            },
            "source_transfer": None,
            "statement_descriptor": None,
            "status": "succeeded"
        }

        httpretty.register_uri(
            httpretty.POST, "https://api.stripe.com/v1/charges",
            body=json.dumps(charges_data),
            status=201
        )

        self.create_customer_and_card('cus_842ErI0D7xCGm1')

        #
        # Create a new charge for the user
        #
        response = self.client.post(
            reverse('api:v1:stripe-charges-list'),
            {
                'currency': 'usd',
                'customer_id': self.customer.id,
                'description': 'testing charge',
                'class_id': self.related_class.id
            },
            format='json'
        )

        #
        # If everything was correct the answer should be a 201 http response
        # with a success message and a charge id. If the charge was cerated in
        # Stripe then is possible to retrieve it
        #

        # Testing information returned from the serializer.
        self.assertEqual(response.data['amount'], "9.99")

        # Checking related class information.
        self.assertEqual(response.data['related_class']['id'], 1)
        self.assertEqual(response.data['related_class']['teacher'], 2)
        self.assertEqual(response.data['related_class']['student'], 2)
        self.assertEqual(response.data['related_class']['subject']['id'], 1)

        created_charge = stripe.Charge.retrieve(response.data.get('charge_id'))

        self.assertEqual(created_charge.amount, 999)
        self.assertEqual(created_charge.currency, 'usd')
        self.assertEqual(created_charge.description, 'testing charge')
        self.assertEqual(created_charge.amount_refunded, 0)
        self.assertEqual(created_charge.source.address_line1_check, None)

    def test_address_line1_is_unavailable_for_the_card(self):
        """
        This test is designed for the card with number 4000 0000 0000 0044
        where the address_line1 and address_zip are unavailable to check that
        the error message is managed correctly. All the customers where
        created with the console, if there is a problem with the customer
        a new token should be generated, a new customer created and the
        customer_id should be replaced.
        """

        charges_data = {
            "id": "ch_185IYD2eZvKYlo2CiprQHol4",
            "object": "charge",
            "amount": 2000,
            "amount_refunded": 0,
            "application_fee": None,
            "balance_transaction": "txn_185IYD2eZvKYlo2CeR0Oax5g",
            "captured": True,
            "created": 1461863021,
            "currency": "usd",
            "customer": "cus_842ErI0D7xCGm1",
            "description": None,
            "destination": None,
            "dispute": None,
            "failure_code": None,
            "failure_message": None,
            "fraud_details": {},
            "invoice": None,
            "livemode": False,
            "metadata": {},
            "order": None,
            "paid": True,
            "receipt_email": None,
            "receipt_number": None,
            "refunded": False,
            "refunds": {
                "object": "list",
                "data": [],
                "has_more": False,
                "total_count": 0,
                "url": "/v1/charges/ch_185IYD2eZvKYlo2CiprQHol4/refunds"
            },
            "shipping": None,
            "source": {
                "id": "card_17nu9mJNKLANSXXXNZlzhQge",
                "object": "card",
                "address_city": None,
                "address_country": None,
                "address_line1": None,
                "address_line1_check": None,
                "address_line2": None,
                "address_state": None,
                "address_zip": None,
                "address_zip_check": None,
                "brand": "Visa",
                "country": "US",
                "customer": "cus_842ErI0D7xCGm1",
                "cvc_check": "pass",
                "dynamic_last4": None,
                "exp_month": 12,
                "exp_year": 2017,
                "fingerprint": "Xt5EWLLDS7FJjR1c",
                "funding": "credit",
                "last4": "4242",
                "metadata": {},
                "name": "Javier Castañeda",
                "tokenization_method": None
            },
            "source_transfer": None,
            "statement_descriptor": None,
            "status": "succeeded"
        }

        httpretty.register_uri(
            httpretty.POST, "https://api.stripe.com/v1/charges",
            body=json.dumps(charges_data),
            status=201
        )

        self.create_customer_and_card('cus_842ErI0D7xCGm1')

        #
        # Create a new charge for the user
        #
        response = self.client.post(
            reverse('api:v1:stripe-charges-list'),
            {
                'currency': 'usd',
                'customer_id': self.customer.id,
                'description': 'testing charge',
                'class_id': 1
            },
            format='json'
        )

        #
        # If everything was correct the answer should be a 201 http response
        # with a success message and a charge id. If the charge was cerated in
        # Stripe then is possible to retrieve it
        #
        self.assertEqual(response.status_code, 201)

        # Testing information returned from the serializer.
        self.assertEqual(response.data['amount'], "9.99")

        # Checking related class information.
        self.assertEqual(response.data['related_class']['id'], 1)
        self.assertEqual(response.data['related_class']['teacher'], 2)
        self.assertEqual(response.data['related_class']['student'], 2)
        self.assertEqual(response.data['related_class']['subject']['id'], 1)

        created_charge = stripe.Charge.retrieve(response.data.get('charge_id'))

        self.assertEqual(created_charge.amount, 999)
        self.assertEqual(created_charge.currency, 'usd')
        self.assertEqual(created_charge.description, 'testing charge')
        self.assertEqual(created_charge.amount_refunded, 0)
        self.assertEqual(created_charge.source.address_line1_check, None)

    @httpretty.activate
    def test_a_charge_is_not_created_when_the_card_is_declined(self):
        """
        This test is designed for the card with number 4000 0000 0000 0019
        where the card is denied to check that
        the error message is managed correctly. All the customers where
        created with the console, if there is a problem with the customer
        a new token should be generated, a new customer created and the
        customer_id should be replaced.
        """

        httpretty.register_uri(
            httpretty.POST, "https://api.stripe.com/v1/charges",
            body="{'error_message':'Your card was declined.'}",
            status=400
        )

        self.create_customer_and_card('cus_85ZAFMAAcIMWZW')

        #
        # Create a new charge for the user
        #
        response = self.client.post(
            reverse('api:v1:stripe-charges-list'),
            {
                'amount': 1050,
                'currency': 'usd',
                'customer_id': self.customer.id,
                'description': 'testing charge',
                'class_id': self.related_class.id
            }
        )

        # #
        # # The expected answer should be a 500 http response
        # # with a error message and a error code.
        # #
        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            response.data.get('error_message'),
            "Your card was declined."
        )

        # self.assertEqual(
        #     response.data.get('error_code'),
        #     'card_declined'
        # )

    def test_a_customer_is_not_created_when_the_cvc_code_is_incorrect(self):
        """
        This test is designed for the card with number 4000 0000 0000 0127
        where the cvc code is incorrect
        the error message is managed correctly. All the customers where
        created with the console, if there is a problem with the customer
        a new token should be generated, a new customer created and the
        customer_id should be replaced.
        """

        with self.assertRaises(stripe.error.CardError):
            stripe.Customer.create(
                source='tok_17pNKiJNKLANSXXXMRIWbCuX',
                description='incorrect cvc code'
            )

    def test_a_customer_is_not_created_when_the_card_is_declines(self):
        """
        This test is designed for the card with number 4000 0000 0000 0002
        where the card is declined
        the error message is managed correctly. All the customers where
        created with the console, if there is a problem with the customer
        a new token should be generated, a new customer created and the
        customer_id should be replaced.
        """

        with self.assertRaises(stripe.error.CardError):
            stripe.Customer.create(
                source='tok_17pNHmJNKLANSXXXBIeWhGvi',
                description='card declined'
            )

    def test_a_customer_is_not_created_when_the_card_has_expired(self):
        """
        This test is designed for the card with number 4000 0000 0000 0069
        where the card is declined
        the error message is managed correctly. All the customers where
        created with the console, if there is a problem with the customer
        a new token should be generated, a new customer created and the
        customer_id should be replaced.
        """

        with self.assertRaises(stripe.error.CardError):
            stripe.Customer.create(
                source='tok_17pNLzJNKLANSXXXIjkm6Iub',
                description='card expired'
            )

    def test_a_customer_is_not_created_when_there_is_a_processing_error(self):
        """
        This test is designed for the card with number 4000 0000 0000 0119
        where the card is declined
        the error message is managed correctly. All the customers where
        created with the console, if there is a problem with the customer
        a new token should be generated, a new customer created and the
        customer_id should be replaced.
        """

        with self.assertRaises(stripe.error.CardError):
            stripe.Customer.create(
                source='tok_17pNMhJNKLANSXXX2j2KPc68',
                description='processing error'
            )

    def test_student_without_a_stripe_customer_cant_receive_a_class(self):
        """
        A user that doesn't have a customer account, avoid teacher to accept
        the class.
        """

        self.create_customer_and_card('cus_842ErI0D7xCGm1')

        #
        # Trying to change the state of the class to accepted
        #
        response = self.client.patch(
            reverse(
                'api:v1:class-detail',
                kwargs={
                    'pk': self.another_class.id
                }
            ),
            {
                'class_status': 3
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data.get('error_message'),
            "Student doesn't have a stripe customer account."
        )

    def test_student_with_a_stripe_customer_can_receive_a_class(self):
        """
        A user that does have a customer account, allows a teacher to accept
        a class and generate a stripe charge.
        """
        self.create_customer_and_card('cus_842ErI0D7xCGm1')

        #
        # Trying to change the state of the class to accepted
        #
        response = self.client.patch(
            reverse(
                'api:v1:class-detail',
                kwargs={
                    'pk': self.related_class.id
                }
            ),
            {
                'class_status': 3
            },
            format='json'
        )

        # A charge was created so, the state should be 201.
        self.assertEqual(response.status_code, 200)

        # Testing information returned from the serializer.
        self.assertEqual(response.data['amount'], "9.99")

        # Checking related class information.
        self.assertEqual(response.data['related_class']['id'], 1)
        self.assertEqual(response.data['related_class']['teacher'], 2)
        self.assertEqual(response.data['related_class']['student'], 2)
        self.assertEqual(response.data['related_class']['subject']['id'], 1)

        created_charge = stripe.Charge.retrieve(
            response.data.get('charge_id')
        )

        self.assertEqual(created_charge.amount, 999)
        self.assertEqual(created_charge.currency, 'usd')
        self.assertEqual(
            created_charge.description,
            'class:1 customer:cus_842ErI0D7xCGm1 amount:9.99'
        )
        self.assertEqual(created_charge.amount_refunded, 0)
        self.assertEqual(created_charge.source.address_line1_check, None)

        created_charge = stripe.Charge.retrieve(response.data.get('charge_id'))

        self.assertEqual(created_charge.amount, 999)
        self.assertEqual(created_charge.currency, 'usd')

        schedule_class = Class.objects.get(id=1)

        # Description used in the stripe charge.
        charge_description = generate_charge_description(
            schedule_class,
            schedule_class.teacher.price_per_hour(schedule_class.subject.id)
        )

        self.assertEqual(created_charge.description, charge_description)

        self.assertEqual(created_charge.amount_refunded, 0)
        self.assertEqual(created_charge.source.address_line1_check, None)

    def test_student_without_a_stripe_customer_cant_receive_a_extension(self):
        """
        A user that doesn't have a customer account, avoid him to accept a
        class extension.
        """

        self.create_customer_and_card('cus_842ErI0D7xCGm1')

        #
        # Trying to change the state of the class extension to accepted.
        #
        response = self.client.patch(
            reverse(
                'api:v1:request-class-extension-time-detail',
                kwargs={
                    'pk': self.class_extension_2.id
                }
            ),
            {
                'accepted': True
            },
            format='json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data.get('error_message'),
            "Student doesn't have a stripe customer account."
        )
