# -*- coding: utf-8 -*-

from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_framework_jwt.views import JSONWebTokenAPIView

from .serializers import (
    ChangePasswordSerializer,
    NewPasswordSerializer,
    RegistrationProfileSerializer,
    RegistrationResultSerializer,
    ResetTokenSerializer
)


class RegistrationProfileViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def create(self, request, format=None):
        """
        Register user
        ---

        type:
          photo:
            required: false
            type: file

        request_serializer: RegistrationProfileSerializer
        response_serializer: RegistrationProfileSerializer
        omit_serializer: false

        parameters_strategy: merge
        omit_parameters:
            - path
        parameters:
            - name: photo
              description: Photo user.
              required: false
              type: file
              paramType: file

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
        serializer = RegistrationProfileSerializer(data=request.data)

        if serializer.is_valid():

            # Save user
            user = serializer.save(
                request=request,
                validated_data=serializer.validated_data)

            # Object user serialization in return for return token.
            user.username = u''.join(str(user.username).decode('utf-8'))

            return Response(
                RegistrationResultSerializer(
                    user,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NewPasswordViewSet(mixins.CreateModelMixin, viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def create(self, request):
        """
        New password
        ---

        type:
          email:
            required: true
            type: string

        request_serializer: NewPasswordSerializer
        response_serializer: NewPasswordSerializer
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

        serializer = NewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create(serializer.data)
            return Response(
                "Mail sent successfully",
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ChangePasswordViewSet(mixins.CreateModelMixin, viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def create(self, request):
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

        request_serializer: ChangePasswordSerializer
        response_serializer: ChangePasswordSerializer
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
        serializer = ChangePasswordSerializer(data=request.data)
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


class ResetTokenViewSet(JSONWebTokenAPIView):
    permission_classes = ()
    authentication_classes = ()

    serializer_class = ResetTokenSerializer
