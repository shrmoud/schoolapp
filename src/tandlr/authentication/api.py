# -*- coding: utf-8 -*-
from rest_framework import status, viewsets
from rest_framework.decorators import detail_route
from rest_framework.response import Response

from tandlr.api.v2.routers import router
from tandlr.core.api.routers.single import SingleObjectRouter

from . import serializers
from .permissions import AuthPermissions


class AuthViewSet(viewsets.GenericViewSet):

    permission_classes = (AuthPermissions, )

    @detail_route(methods=['POST'])
    def login(self, request, *args, **kwargs):
        """
        Logs the user in.
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
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.create(serializer.data)

            login_response_serializer = serializers.LoginResponseV2Serializer(
                user
            )
            return Response(login_response_serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['POST'])
    def logout(self, request, *args, **kwargs):
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

    def get_serializer_class(self):
        """
        Returns the proper serializer for the current request.
        """
        if self.action == 'login':
            return serializers.LoginSerializer

        elif self.action == 'logout':
            return serializers.LogoutSerializer


router.register(
    r'auth',
    AuthViewSet,
    base_name="auth",
    router_class=SingleObjectRouter
)
