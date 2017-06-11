# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from tandlr.api.v2. routers import router
from tandlr.core.api import mixins, viewsets
from tandlr.core.api.routers.single import SingleObjectRouter
from tandlr.registration.models import User
from tandlr.registration.serializers import (
    ChangePasswordV2Serializer,
    NewPasswordV2Serializer,
    RegistrationProfileV2Serializer,
    RegistrationResultV2Serializer,
)


class RegistrationViewset(
        mixins.CreateModelMixin,
        viewsets.GenericViewSet):

    permission_classes = (AllowAny,)

    create_serializer_class = RegistrationProfileV2Serializer
    retrieve_serializer_class = RegistrationResultV2Serializer

    def get_queryset(self):
        return User.objects.all()

    def create(self, request):
        """
        Register user
        ---

        type:
          photo:
            required: false
            type: file

        request_serializer: RegistrationProfileV2Serializer
        response_serializer: RegistrationProfileV2Serializer
        omit_serializer: false

        parameters_strategy: merge
        omit_parameters:
            - path

        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 201
              message: CREATED
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(RegistrationViewset, self).create(request)

    def perform_create(self, serializer):
        request = self.request
        validated_data = serializer.validated_data
        return serializer.save(request, validated_data)


class PasswordViewset(viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_class = NewPasswordV2Serializer

    @detail_route(methods=['POST'])
    def new_password(self, request):
        """
        New password
        ---

        type:
          email:
            required: true
            type: string

        request_serializer: NewPasswordV2Serializer
        omit_serializer: true

        parameters_strategy: merge
        parameters:
            - name: email
              description: User mail.
              required: true
              type: string
              paramType: form

        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 201
              message: CREATED
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.create(serializer.data)
            return Response(
                {
                    'detail': 'Mail sent successfully'
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    @detail_route(methods=['POST'])
    def change_password(self, request):
        """
        Change password
        ---

        type:
          email:
            required: true
            type: string
          token:
            required: true
            type: string

        request_serializer: ChangePasswordV2Serializer
        omit_serializer: false

        parameters:
            - name: email
              description: User mail.
              required: true
              type: string
              paramType: form
            - name: token
              description: token validation.
              required: true
              type: string
              paramType: form

        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 200
              message: OK
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.create(serializer.data)
            return Response(
                "Password successfully changed",
                status=status.HTTP_200_OK
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def get_serializer_class(self, action=None):
        """
        Returns the proper serializer for the current request.
        """
        if self.action == 'new_password':
            return NewPasswordV2Serializer

        elif self.action == 'change_password':
            return ChangePasswordV2Serializer


router.register(
    r'auth/signup',
    RegistrationViewset,
    base_name="registration",
)

router.register(
    r'auth',
    PasswordViewset,
    base_name="auth",
    router_class=SingleObjectRouter
)
