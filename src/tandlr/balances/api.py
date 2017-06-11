# -*- coding: utf-8 -*-
"""
viewsets to manage balances in tandlr.
"""
from tandlr.api.v2.routers import router
from tandlr.balances.models import Balance
from tandlr.balances.permissions import BalancePermission
from tandlr.balances.serializers import (
    BalanceBillsV2Serializer,
    BalanceV2Serializer
)
from tandlr.core.api import mixins, viewsets
from tandlr.scheduled_classes.models import ClassBill
from tandlr.scheduled_classes.serializers import (
    HistorySessionBillsV2Serializer
)


class BalanceViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    serializer_class = BalanceV2Serializer
    list_serializer_class = BalanceV2Serializer
    retrieve_serializer_class = BalanceV2Serializer

    permission_classes = (BalancePermission,)

    def get_queryset(self):
        return Balance.objects.filter(
            teacher=self.request.user
        )

    def list(self, request, *args, **kwargs):
        """
        Allows the session's teacher to get all the information for his balance
        ---
        request_serializer: BalanceV2Serializer
        response_serializer: BalanceV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(BalanceViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Allows the session's teacher to get all the information for his balance
        ---
        request_serializer: BalanceV2Serializer
        response_serializer: BalanceV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(BalanceViewSet, self).retrieve(request, *args, **kwargs)


class BalanceHistoryBillsViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    serializer_class = HistorySessionBillsV2Serializer
    list_serializer_class = HistorySessionBillsV2Serializer
    retrieve_serializer_class = HistorySessionBillsV2Serializer

    permission_classes = (BalancePermission,)

    def get_queryset(self):
        return ClassBill.objects.filter(
            balance__teacher=self.request.user
        )

    def list(self, request, *args, **kwargs):
        """
        Allows the session's teacher to get all the history for his balance
        bills
        ---
        request_serializer: HistorySessionBillsV2Serializer
        response_serializer: HistorySessionBillsV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(BalanceHistoryBillsViewSet, self).list(
            request,
            *args,
            **kwargs
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Allows the session's teacher to get all the history for his balance
        bills
        ---
        request_serializer: HistorySessionBillsV2Serializer
        response_serializer: HistorySessionBillsV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(BalanceHistoryBillsViewSet, self).retrieve(
            request,
            *args,
            **kwargs
        )


class BalanceBillsViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    serializer_class = BalanceBillsV2Serializer
    list_serializer_class = BalanceBillsV2Serializer
    retrieve_serializer_class = BalanceBillsV2Serializer

    permission_classes = (BalancePermission,)

    def get_queryset(self):
        return ClassBill.objects.filter(
            balance__teacher=self.request.user
        )

    def list(self, request, *args, **kwargs):
        """
        Allows the session's teacher to get the information of all his bills.
        ---
        request_serializer: BalanceBillsV2Serializer
        response_serializer: BalanceBillsV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(BalanceBillsViewSet, self).list(
            request,
            *args,
            **kwargs
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Allows the session's teacher to get the information of all his bills.
        ---
        request_serializer: BalanceBillsV2Serializer
        response_serializer: BalanceBillsV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(BalanceBillsViewSet, self).retrieve(
            request,
            *args,
            **kwargs
        )


router.register(
    r'balances',
    BalanceViewSet,
    base_name='balances'
)

router.register(
    r'history',
    BalanceHistoryBillsViewSet,
    base_name='history'
)

router.register(
    r'balances-bills',
    BalanceBillsViewSet,
    base_name='balances-bills'
)
