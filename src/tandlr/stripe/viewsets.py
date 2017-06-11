# -*- coding: utf-8 -*-
import datetime

from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

import stripe

from tandlr.scheduled_classes.models import Class
from tandlr.scheduled_classes.utils import calculate_price_per_extrension_class
from tandlr.stripe.models import StripeCard, StripeCharge, StripeCustomer
from tandlr.stripe.serializers import (
    StripeCardSerializer,
    StripeChargeSerializer,
    StripeCreateCardSerializer,
    StripeCreateChargeSerializer,
    StripeCreateCustomerSerializer,
    StripeCreatedCustomerSerializer
)

from .utils import (
    create_stripe_card,
    create_stripe_customer,
    make_stripe_charge
)


class StripeCustomerViewSet(ViewSet):

    def retrieve(self, request, pk=None):
        """
        Get customer information by customer_id or user id.
        ---

        serializer: StripeCreatedCustomerSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
            - code: 201
              message: CREATED
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """

        # If is a digit, the PK is a id.
        if pk.isdigit():
            customer = get_object_or_404(StripeCustomer, user__id=pk)
        # Else, is a customer_id
        else:
            customer = get_object_or_404(StripeCustomer, customer_id=pk)

        serializer = StripeCreatedCustomerSerializer(customer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, format=None):
        """
        Creates a customer with a given card_token and an optional description.
        ---

        request_serializer: StripeCreateCustomerSerializer
        response_serializer: StripeCreatedCustomerSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
            - code: 201
              message: CREATED
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        serializer = StripeCreateCustomerSerializer(data=request.data)

        if serializer.is_valid():

            # Creating customer on stripe.
            stripe_customer_response = create_stripe_customer(
                request.user,
                serializer.data.get('card_token'),
                serializer.data.get('description')
            )

            # If the creation of the customer was successful.
            if stripe_customer_response['success']:
                created_customer = StripeCreatedCustomerSerializer(
                    stripe_customer_response['response']
                )

                return Response(
                    created_customer.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    stripe_customer_response['response'],
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class StripeChargeViewSet(ViewSet):

    def list(self, request):
        """
        Return list of charges for a given user
        (username or email needed as querystring params).
        ---

        serializer: StripeChargeSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
            - code: 201
              message: CREATED
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        queryset = StripeCharge.objects.filter(
            Q(customer__user__username=request.GET.get('username', None)) |
            Q(customer__user__email=request.GET.get('email', None))
        )

        paginator = PageNumberPagination()

        result_page = paginator.paginate_queryset(queryset, request)

        serializer = StripeChargeSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def create(self, request, format=None):
        """
        Creates a charge for a user, with a given customer_id, amount
        and class_id.
        ---

        serializer: StripeChargeSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
            - code: 201
              message: CREATED
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        serializer = StripeCreateChargeSerializer(data=request.data)

        if serializer.is_valid():
            #
            # If the application sends a token create a complete new
            # charge, otherwise charge the user again with the customer_id
            #

            # Scheduled class.
            schedule_class = get_object_or_404(
                Class, pk=serializer.data.get('class_id')
            )

            # Right now, duration is not given in the
            # serializer information, so let's assume that is just an hour.
            time = datetime.time(1, 0, 0)

            amount = calculate_price_per_extrension_class(
                schedule_class.teacher.price_per_hour(
                    schedule_class.subject.id
                ),
                time
            )

            # making the stripe charge
            stripe_charge_response = make_stripe_charge(
                serializer.data.get('class_id'),
                int(amount * 100),  # amount
                serializer.data.get('currency', 'usd'),
                serializer.data.get('description', ''),
                serializer.data.get('customer_id'),
                serializer.data.get('card_token')
            )

            # If the creation of the charge was successful.
            if stripe_charge_response['success']:
                created_charge = StripeChargeSerializer(
                    stripe_charge_response['response']
                )

                return Response(
                    created_charge.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    stripe_charge_response['response'],
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class StripeCardViewSet(ViewSet):

    def retrieve(self, request, pk=None):
        """
        Get card by card_id.
        ---

        serializer: StripeCardSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
            - code: 201
              message: CREATED
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """

        card = get_object_or_404(StripeCard, card_id=pk)

        serializer = StripeCardSerializer(card)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, format=None):
        """
        Creates a new card for a user, with a given card_token and customer_id.
        ---

        request_serializer: StripeCreateCardSerializer
        response_serializer: StripeCardSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
            - code: 201
              message: CREATED
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        stripe.api_key = settings.STRIPE_PRIVATE_KEY

        serializer = StripeCreateCardSerializer(data=request.data)

        if serializer.is_valid():
            stripe_card_response = create_stripe_card(
                serializer.data.get('customer_id'),
                serializer.data.get('card_token')
            )

            # If the creation of the card was successful.
            if stripe_card_response['success']:
                created_card = StripeCardSerializer(
                    stripe_card_response['response']
                )

                return Response(
                    created_card.data,
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    stripe_card_response['response'],
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
