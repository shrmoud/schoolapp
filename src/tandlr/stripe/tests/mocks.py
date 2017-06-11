# -*- coding: utf-8 -*-

import json


class MockCustomer():

    def getCustomer(self):
        return json.dumps(
            {
                "account_balance": 0,
                "created": 1457717708,
                "currency": None,
                "default_source": "card_17nu9mJNKLANSXXXNZlzhQge",
                "delinquent": False,
                "description": "testing customer id",
                "discount": None,
                "email": None,
                "id": "cus_842ErI0D7xCGm1",
                "livemode": False,
                "metadata": {},
                "object": "customer",
                "shipping": None,
                "sources": {
                    "data": [
                        {
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
                            "customer": "cus_842ErI0D7xCGm1",
                            "cvc_check": "pass",
                            "dynamic_last4": None,
                            "exp_month": 4,
                            "exp_year": 2018,
                            "fingerprint": "4fOLwxz2ZQeKZPAN",
                            "funding": "credit",
                            "id": "card_17nu9mJNKLANSXXXNZlzhQge",
                            "last4": "4444",
                            "metadata": {},
                            "name": "Javier Casta\u00f1eda",
                            "object": "card",
                            "tokenization_method": None,
                        }
                    ],
                    "has_more": False,
                    "object": "list",
                    "total_count": 1,
                    "url": "/v1/customers/cus_842ErI0D7xCGm1/sources"
                },
                "subscriptions": {
                    "data": [],
                    "has_more": False,
                    "object": "list",
                    "total_count": 0,
                    "url": "/v1/customers/cus_842ErI0D7xCGm1/subscriptions"
                }
            }
        )


class MockCharge():

    def getCharge(self):
        return json.dumps(
            {
                "amount": 100,
                "amount_refunded": 0,
                "application_fee": None,
                "balance_transaction": "txn_17nvZ6JNKLANSXXXrQVXxsas",
                "captured": True,
                "created": 1457723088,
                "currency": "usd",
                "customer": "cus_842ErI0D7xCGm1",
                "description": "a",
                "destination": None,
                "dispute": None,
                "failure_code": None,
                "failure_message": None,
                "fraud_details": {},
                "id": "ch_17nvZ6JNKLANSXXXbD3LJmnj",
                "invoice": None,
                "livemode": False,
                "metadata": {},
                "object": "charge",
                "order": None,
                "paid": True,
                "receipt_email": None,
                "receipt_number": None,
                "refunded": False,
                "refunds": {
                    "data": [],
                    "has_more": False,
                    "object": "list",
                    "total_count": 0,
                    "url": (
                        "/v1/charges/ch_17nvZ6JNKLANSXXXbD3LJmnj/refunds"
                    )
                },
                "shipping": None,
                "source": {
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
                    "customer": "cus_842ErI0D7xCGm1",
                    "cvc_check": None,
                    "dynamic_last4": None,
                    "exp_month": 4,
                    "exp_year": 2018,
                    "fingerprint": "4fOLwxz2ZQeKZPAN",
                    "funding": "credit",
                    "id": "card_17nu9mJNKLANSXXXNZlzhQge",
                    "last4": "4444",
                    "metadata": {},
                    "name": "Javier Casta\u00f1eda",
                    "object": "card",
                    "tokenization_method": None,
                },
                "source_transfer": None,
                "statement_descriptor": None,
                "status": "succeeded"
            }
        )


class MockCard():

    def getCard(self):
        return json.dumps(
            {
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
                "customer": "cus_842ErI0D7xCGm1",
                "cvc_check": "pass",
                "dynamic_last4": None,
                "exp_month": 4,
                "exp_year": 2018,
                "fingerprint": "4fOLwxz2ZQeKZPAN",
                "funding": "credit",
                "id": "card_17nu9mJNKLANSXXXNZlzhQge",
                "last4": "4444",
                "metadata": {},
                "name": "Javier Casta\u00f1eda",
                "object": "card",
                "tokenization_method": None
            }
        )
