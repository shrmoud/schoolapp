# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response

import stripe

from tandlr.scheduled_classes.models import Class
from tandlr.stripe.models import StripeCard, StripeCharge, StripeCustomer


def generate_exception_response(error_message, error_code):
    return {
        'success': False,
        'response': {
            'error_message': error_message,
            'error_code': error_code
        }
    }


def generate_success_response(response_object):
    return {
        'success': True,
        'response': response_object
    }


def generate_charge_description(scheduled_class, amount):
    return 'class:{0} customer:{1} amount:{2}'.format(
        scheduled_class.id,
        scheduled_class.student.customer_id,
        amount
    )


def create_stripe_customer(user, card_token, description):
    """
    Creates an stripe customer by giving the following information:
        * user
        * card_token
        * description (optional)

    """
    stripe.api_key = settings.STRIPE_PRIVATE_KEY

    try:
        customer = stripe.Customer.create(
            source=card_token,
            description=description
        )

        stripe_customer = StripeCustomer.objects.create(
            user=user,
            account_balance=customer.account_balance,
            delinquent=customer.delinquent,
            default_source=customer.default_source,
            customer_id=customer.id
        )

        cards = []
        for card in customer.sources.data:
            cards.append(
                StripeCard.objects.create(
                    customer=stripe_customer,
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

        return generate_success_response(stripe_customer)

    except stripe.error.CardError as e:
        # The card has been declined
        return generate_exception_response(e.message, e.code)

    except stripe.error.APIConnectionError as e:
        # Failure to connecr to Stripe's API
        return generate_exception_response(e.message, e.code)

    except stripe.error.AuthenticationError as e:
        # Failure to properly authenticate the user in the request
        return generate_exception_response(e.message, e.code)

    except stripe.error.RateLimitError as e:
        # Too many request hit to the API of Stripe
        return generate_exception_response(e.message, e.code)

    except stripe.error.StripeError as e:
        # Generic error for the user
        return generate_exception_response(e.message, 'stripe error.')

    except Exception as e:
        # Catch any other problem for the charge
        return generate_exception_response(e.message, 'tandlr error.')


def create_stripe_card(customer_id, card_token):
    """
    Creates an stripe customer by giving the following information:
        * customer_id
        * card_token
    """
    stripe.api_key = settings.STRIPE_PRIVATE_KEY
    try:
        customer = stripe.Customer.retrieve(customer_id)

        # Creating a card with a given
        card = customer.sources.create(
            source=card_token
        )

        stripe_customer = StripeCustomer.objects.get(
            customer_id=customer.id
        )

        stripe_card = StripeCard.objects.create(
            customer=stripe_customer,
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

        return generate_success_response(stripe_card)

    except stripe.error.RateLimitError as e:
        # Too many request hit to the API of Stripe
        return Response(
            e.message, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    except Exception as e:
        # Catch any other problem for the charge
        return Response(
            e.message, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def make_stripe_charge(
    class_id,
    amount,
    currency,
    description,
    customer_id,
    card_token
):
    """
    Makes a stripe change by giving the following information:
        * class_id
        * amount
        * currency
        * description (optional)
        * customer_id (optional could be customer_id or card_token)
        * card_token (optional could be customer_id or card_token)
    """
    stripe.api_key = settings.STRIPE_PRIVATE_KEY

    try:
        related_class = get_object_or_404(
            Class,
            id=class_id
        )

        if (card_token):
            charge = stripe.Charge.create(
                source=card_token,
                amount=amount,
                currency=currency,
                description=description,
            )
        elif (customer_id):
            charge = stripe.Charge.create(
                amount=amount,
                currency=currency,
                customer=customer_id,
                description=description,
            )

        stripe_customer = StripeCustomer.objects.get(
            customer_id=customer_id
        )

        stripe_card = StripeCard.objects.get(card_id=charge.source.id)

        # Stripe receives the amount in cents, but the tandlr saves it normaly.
        amount = amount / 100.00

        stripe_charge = StripeCharge.objects.create(
            customer=stripe_customer,
            card=stripe_card,
            currency=charge.currency,
            amount=amount,
            amount_refunded=charge.amount_refunded,
            paid=charge.paid,
            disputed=charge.dispute,
            refunded=charge.refunded,
            captured=charge.captured,
            charge_id=charge.id,
            related_class=related_class,
            description=description
        )

        return generate_success_response(stripe_charge)

    except stripe.error.CardError as e:
        # The card has been declined
        return generate_exception_response(e.message, e.code)

    except stripe.error.APIConnectionError as e:
        # Failure to connecr to Stripe's API
        return generate_exception_response(e.message, e.code)

    except stripe.error.AuthenticationError as e:
        # Failure to properly authenticate the user in the request
        return generate_exception_response(e.message, e.code)

    except stripe.error.RateLimitError as e:
        # Too many request hit to the API of Stripe
        return generate_exception_response(e.message, e.code)

    except stripe.error.StripeError as e:
        # Generic error for the user
        return generate_exception_response(e.message, 'stripe error.')

    except Exception as e:
        # Catch any other problem for the charge
        return generate_exception_response(e.message, 'tandlr error.')


def create_card(card, customer, is_default=False):
    """
    Function to create the bank card data returns stripe
        * card
        * customer
        * is_default
    """
    card = StripeCard.objects.create(
        customer=customer,
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
        card_id=card.id,
        is_default=is_default
    )
    return card
