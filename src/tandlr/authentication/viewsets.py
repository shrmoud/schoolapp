# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from . import serializers


class LoginViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny, )

    def create(self, request, format=None):
        """
        Login
        ---
        type:
          email:
            required: true
            type: string
          password:
            required: true
            type: string
          device_os:
            required: true
            type: string
          device_user_token:
            required: false
            type: string

        parameters:
            - name: email
              description: email user.
              required: true
              type: string
              paramType: form
            - name: password
              description: Password for acces Tandlr.
              required: true
              type: string
              paramType: form
            - name: device_os
              required: true
              description: Mobile operating system device user.
              type: string
              paramType: form
            - name: device_user_token
              description: Device token.
              required: false
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
        serializer = serializers.LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.create(serializer.data)

            perfil_serializer = serializers.UserProfileDetailSerializer(
                user,
                context={'request': request}
            )

            return Response(perfil_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutViewSet(viewsets.GenericViewSet):
    """
    Viewset to handle user's logout.
    """
    serializer_class = serializers.LogoutSerializer

    def create(self, request, *args, **kwargs):
        """
        Logs the user out, disabling the given device.
        ---
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
            serializer.update()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
