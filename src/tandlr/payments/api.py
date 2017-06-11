# -*- coding: utf-8 -*-
"""
viewsets to manage session in tandlr.
"""
from rest_framework.generics import get_object_or_404

from tandlr.core.api import mixins, viewsets
from tandlr.payments.models import TeacherPaymentInformation
from tandlr.payments.permissions import TeacherPaymentInformationPermission
from tandlr.payments.serializers import TeacherPaymentInformationV2Serializer


class TeacherPaymentInformationViewSet(
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    permission_classes = (TeacherPaymentInformationPermission,)

    serializer_class = TeacherPaymentInformationV2Serializer
    retrieve_serializer_class = TeacherPaymentInformationV2Serializer

    def retrieve(self, request, *args, **kwargs):
        """
        Allows the session's user get the information for certain slot.
        ---
        request_serializer: TeacherPaymentInformationV2Serializer
        response_serializer: TeacherPaymentInformationV2Serializer

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
        return super(
            TeacherPaymentInformationViewSet,
            self
        ).retrieve(
            request,
            *args,
            **kwargs
        )

    def get_object(self):
        return get_object_or_404(
            TeacherPaymentInformation,
            teacher=self.request.user
        )
