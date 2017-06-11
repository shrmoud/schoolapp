# -*- coding: utf-8 -*-
from django.conf import settings

from rest_framework import serializers

import stripe

from tandlr.core.api.serializers.base import ModelSerializer
from tandlr.scheduled_classes.serializers import (
    ClassDetailSerializer,
    ClassDetailV2Serializer
)
from tandlr.stripe.models import (
    StripeCard,
    StripeCharge,
    StripeCustomer
)
from tandlr.users.serializers import UserStripeDetailSerializer

from .utils import generate_exception_response


class StripeCustomerSerializer(serializers.ModelSerializer):
    """
    Serializer to show customer details.
    """
    user = UserStripeDetailSerializer()

    class Meta:
        model = StripeCustomer
        fields = (
            'customer_id',
            'user',
        )


class StripeCardSerializer(serializers.ModelSerializer):
    """
    Serializer to show stripe card details.
    """

    customer = StripeCustomerSerializer()

    class Meta:
        model = StripeCard
        fields = (
            'brand',
            'card_id',
            'customer',
            'last4',
            'name',
        )


class StripeCreateChargeSerializer(serializers.Serializer):
    """
    Serializer used only to create a charge.
    """
    customer_id = serializers.CharField(required=False)
    card_token = serializers.CharField(required=False)
    class_id = serializers.IntegerField()
    currency = serializers.CharField(
        required=False,
        default='usd'
    )
    description = serializers.CharField(
        required=False,
        default=''
    )


class StripeChargeSerializer(serializers.ModelSerializer):

    related_class = ClassDetailSerializer()
    card = StripeCardSerializer()

    class Meta:
        model = StripeCharge
        fields = (
            'charge_id',
            'currency',
            'amount',
            'description',
            'paid',
            'disputed',
            'refunded',
            'captured',
            'created_at',
            'related_class',
            'card'
        )


class StripeCreateCustomerSerializer(serializers.Serializer):

    card_token = serializers.CharField()
    description = serializers.CharField(required=False)

    class Meta:
        fields = (
            'card_token',
            'description',
        )


class StripeCreateCardSerializer(serializers.Serializer):

    card_token = serializers.CharField()
    customer_id = serializers.CharField()

    class Meta:
        fields = (
            'card_token',
            'customer_id',
        )


class StripeCreatedCustomerSerializer(serializers.ModelSerializer):

    cards = serializers.SerializerMethodField()

    class Meta:
        model = StripeCustomer
        fields = (
            'customer_id',
            'cards',
        )

    def get_cards(self, instance):
        customer_cards = StripeCard.objects.filter(
            customer__customer_id=instance.customer_id
        )
        return StripeCardSerializer(customer_cards, many=True).data


class CardSerializer(serializers.ModelSerializer):
    """
    Serializer to show stripe card details.
    """

    customer = StripeCustomerSerializer()
    last_four_digits = serializers.CharField(
        source='last4',
        max_length=4,
        min_length=4
    )

    class Meta:
        model = StripeCard
        fields = (
            'brand',
            'card_id',
            'customer',
            'is_default'
            'last_four_digits',
            'name',
        )


class CreateCardSerializer(serializers.Serializer):

    card_token = serializers.CharField()
    description = serializers.CharField(required=False)
    default = serializers.BooleanField(default=False)

    class Meta:
        fields = (
            'card_token',
            'description',
            'default'
        )

    def create(self, validated_data):
        from tandlr.stripe.utils import create_card
        user = self.context.get('request').user
        card_token = validated_data.get('card_token')
        description = validated_data.get('description', None)
        default_card = validated_data.get('default')
        stripe.api_key = settings.STRIPE_PRIVATE_KEY

        try:

            stripe_customer, created = StripeCustomer.objects.get_or_create(
                user=user
            )

            if created:

                customer = stripe.Customer.create(
                    source=card_token,
                    description=description
                )
                stripe_customer.account_balance = customer.account_balance
                stripe_customer.delinquent = customer.delinquent
                stripe_customer.default_source = customer.default_source
                stripe_customer.customer_id = customer.id
                stripe_customer.save()

                for card in customer.sources.data:
                    bank_card = create_card(
                        card=card,
                        customer=stripe_customer,
                        is_default=True)
            else:

                customer = stripe.Customer.retrieve(
                    stripe_customer.customer_id)
                card = customer.sources.create(source=card_token)
                bank_card = create_card(
                    card=card,
                    customer=stripe_customer,
                    is_default=default_card
                )
                if default_card:
                    customer.default_source = card.id
                    customer.save()
                    StripeCard.objects.exclude(
                        id=bank_card.id).update(
                        is_default=False
                    )

            return bank_card

        except stripe.error.CardError as e:
            # The card has been declined
            return generate_exception_response(e.message, e.code)

        except stripe.error.APIConnectionError as e:
            # Failure to connect to Stripe's API
            return generate_exception_response(e.message, e.code)

        except stripe.error.StripeError as e:
            # Generic error for the user
            return generate_exception_response(e.message, 'stripe error.')


class SingleCardSerializer(serializers.ModelSerializer):
    """
    Serializer to show stripe card details.
    """
    last_four_digits = serializers.CharField(
        source='last4',
        max_length=4,
        min_length=4
    )

    class Meta:
        model = StripeCard
        fields = (
            'id',
            'brand',
            'is_default',
            'last_four_digits',
            'name',
            'exp_month',
            'exp_year'
        )


class DefaultCardSerializer(serializers.ModelSerializer):
    """
    Serializer to show stripe card details.
    """
    class Meta:
        model = StripeCard
        fields = (
            'is_default',
        )

    def update(self, instance, validated_data):
        user = self.context.get('request').user
        card = instance
        stripe.api_key = settings.STRIPE_PRIVATE_KEY

        try:
            customer = stripe.Customer.retrieve(
                card.customer.customer_id
            )
            customer.default_source = card.card_id
            customer.save()

            StripeCard.objects.filter(
                customer__user=user,
                is_active=True
            ).exclude(
                id=card.id
            ).update(
                is_default=False
            )

            card.is_default = True
            card.save()

            card.customer.default_source = card.card_id
            card.customer.save()

            return card

        except stripe.error.CardError as e:
            # The card has been declined
            return generate_exception_response(e.message, e.code)

        except stripe.error.APIConnectionError as e:
            # Failure to connect to Stripe's API
            return generate_exception_response(e.message, e.code)

        except stripe.error.StripeError as e:
            # Generic error for the user
            return generate_exception_response(e.message, 'stripe error.')


#
# SerializersV2
#
class StripeCardV2Serializer(serializers.ModelSerializer):
    """
    Serializer to show stripe card details.
    """

    customer = StripeCustomerSerializer()

    class Meta:
        model = StripeCard
        fields = (
            'brand',
            'card_id',
            'customer',
            'last4',
            'name',
        )


class StripeChargeV2Serializer(ModelSerializer):

    related_class = ClassDetailV2Serializer()
    card = StripeCardV2Serializer()

    class Meta:
        model = StripeCharge
        fields = (
            'charge_id',
            'currency',
            'amount',
            'description',
            'paid',
            'disputed',
            'refunded',
            'captured',
            'created_at',
            'related_class',
            'card'
        )
