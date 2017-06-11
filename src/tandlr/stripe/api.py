# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response

import stripe

from tandlr.api.v2.routers import router
from tandlr.core.api import mixins
from tandlr.core.api import viewsets
from tandlr.stripe.models import StripeCard, StripeCharge
from tandlr.stripe.serializers import (
    CreateCardSerializer,
    DefaultCardSerializer,
    SingleCardSerializer,
    StripeChargeV2Serializer
)


class CardViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.PartialUpdateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):

    serializer_class = SingleCardSerializer
    list_serializer_class = SingleCardSerializer
    retrieve_serializer_class = SingleCardSerializer
    create_serializer_class = CreateCardSerializer
    update_serializer_class = DefaultCardSerializer

    def list(self, request):
        """
        List all active user cards for stripe.
        ---

        response_serializer: SingleCardSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
            - code: 403
              message: FORBIDDEN
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(CardViewSet, self).list(request)

    def retrieve(self, request, pk=None):
        """
        Get a data card users for stripe.
        ---

        response_serializer: SingleCardSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
            - code: 403
              message: FORBIDDEN
            - code: 404
              message: NOT FOUND
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(CardViewSet, self).retrieve(request)

    def create(self, request):
        """
        Create card and customer user for stripe.
        ---

        request_serializer: CreateCardSerializer
        response_serializer: SingleCardSerializer
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
        return super(CardViewSet, self).create(request)

    def partial_update(self, request, pk=None):
        """
        Update card to designate as default
        ---

        request_serializer: DefaultCardSerializer
        response_serializer: SingleCardSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
            - code: 400
              message: BAD REQUEST
            - code: 404
              message: NOT FOUND
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(CardViewSet, self).partial_update(request)

    def destroy(self, request, pk=None):
        """
        Delete card.
        ---
        omit_serializer: true

        responseMessages:
            - code: 204
              message: NO CONTENT
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        try:
            stripe.api_key = settings.STRIPE_PRIVATE_KEY
            card = self.get_object()
            customer = stripe.Customer.retrieve(
                card.customer.customer_id
            )

            customer.sources.retrieve(
                card.card_id
            ).delete()

            if card.is_default:
                customer = stripe.Customer.retrieve(
                    card.customer.customer_id
                )
                if customer.default_source:
                    new_default_card = get_object_or_404(
                        StripeCard, card_id=customer.default_source
                    )
                    new_default_card.is_default = True
                    new_default_card.save()

            card.is_active = False
            card.is_default = False
            card.card_id = None
            card.save()

            return Response(
                status=status.HTTP_204_NO_CONTENT
            )

        except stripe.error.CardError as e:
            # The card has been declined
            return Response(
                e.message, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except stripe.error.APIConnectionError as e:
            # Failure to connect to Stripe's API
            return Response(
                e.message, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        except stripe.error.StripeError as e:
            # Generic error for the user
            return Response(
                e.message, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def get_queryset(self):
        return StripeCard.objects.filter(
            customer__user=self.request.user,
            is_active=True
        )


class StripeChargeViewSet(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    serializer_class = StripeChargeV2Serializer
    list_serializer_class = StripeChargeV2Serializer

    def get_queryset(self):
        email = self.request.user.email
        return StripeCharge.objects.filter(
            customer__user__email=email
        )

    def list(self, request):
        """
        Return list of charges for a given user
        ---
        request_serializer: StripeChargeV2Serializer
        response_serializer: StripeChargeV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 403
              message: FORBIDDEN
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(StripeChargeViewSet, self).list(request)


router.register(
    r'cards',
    CardViewSet,
    base_name="cards",
)


router.register(
    r'me/charges-history',
    StripeChargeViewSet,
    base_name="charges-history"
)
