# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from tandlr.security_configuration.models import (
    Permission,
    PermissionRole,
    Role,
    RoleUser
)

from tandlr.security_configuration.serializers import (
    PermissionRoleSerializer,
    PermissionSerializer,
    RoleSerializer,
    RoleUserDetailSerializer,
    RoleUserSerializer
)


class RoleViewSet(viewsets.ModelViewSet):
    serializer_class = RoleSerializer
    queryset = Role.objects.all()


class RoleUserViewSet(viewsets.ViewSet):
    """
    Configuration role by user.
    """

    def list(self, request):
        """
        Configuration role by user.
        ---

        serializer: RoleUserSerializer
        response_serializer: RoleUserDetailSerializer
        omit_serializer: false

        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 200
              message: OK
            - code: 201
              message: CREATED
            - code: 500
              message: INTERNAL SERVER ERROR
        consumes:
            - application/json
        produces:
            - application/json
        """

        queryset = RoleUser.objects.all()

        serializer = RoleUserDetailSerializer(
            queryset,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data)

    def create(self, request):
        """
        Configuration role by user.
        ---

        serializer: RoleUserSerializer
        response_serializer: RoleUserDetailSerializer
        omit_serializer: false

        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 200
              message: OK
            - code: 201
              message: CREATED
            - code: 500
              message: INTERNAL SERVER ERROR
        consumes:
            - application/json
        produces:
            - application/json
        """

        serializer = RoleUserSerializer(data=request.data)

        if serializer.is_valid():

            # Save instance in var.
            role_user = serializer.save()

            # Serialization response with complete object user and role.
            return Response(
                RoleUserDetailSerializer(
                    role_user,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Configuration role by user.
        ---

        serializer: RoleUserSerializer
        response_serializer: RoleUserDetailSerializer
        omit_serializer: false

        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 200
              message: OK
            - code: 201
              message: CREATED
            - code: 500
              message: INTERNAL SERVER ERROR
        consumes:
            - application/json
        produces:
            - application/json
        """

        queryset = RoleUser.objects.filter()

        role_user = get_object_or_404(queryset, pk=pk)

        serializer = RoleUserDetailSerializer(
            role_user,
            context={'request': request}
        )

        return Response(serializer.data)

    def update(self, request, pk=None):
        """
        Configuration role by user.
        ---

        serializer: RoleUserSerializer
        response_serializer: RoleUserDetailSerializer
        omit_serializer: false

        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 200
              message: OK
            - code: 201
              message: CREATED
            - code: 500
              message: INTERNAL SERVER ERROR
        consumes:
            - application/json
        produces:
            - application/json
        """

        role_user = get_object_or_404(RoleUser, pk=pk)

        serializer = RoleUserSerializer(role_user, data=request.data)

        if serializer.is_valid():

            # Save instance in var.
            role_user = serializer.save()

            # Serialization with complete object user and role.
            return Response(
                RoleUserDetailSerializer(
                    role_user,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        """
        Configuration role by user.
        ---

        serializer: RoleUserSerializer
        response_serializer: RoleUserDetailSerializer
        omit_serializer: false

        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 200
              message: OK
            - code: 201
              message: CREATED
            - code: 500
              message: INTERNAL SERVER ERROR
        consumes:
            - application/json
        produces:
            - application/json
        """

        role_user = get_object_or_404(RoleUser, pk=pk)

        serializer = RoleUserSerializer(
            role_user, data=request.data, partial=True)

        if serializer.is_valid():

            # Save instance in var
            role_user = serializer.save()

            # Serialization response with complete object user and role.
            return Response(
                RoleUserDetailSerializer(
                    role_user,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Configuration role by user.
        ---

        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 200
              message: OK
            - code: 201
              message: CREATED
            - code: 500
              message: INTERNAL SERVER ERROR
        consumes:
            - application/json
        produces:
            - application/json
        """

        role_user = get_object_or_404(RoleUser, pk=pk)

        role_user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class PermissionViewSet(viewsets.ModelViewSet):
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()


class PermissionRoleViewSet(viewsets.ModelViewSet):
    serializer_class = PermissionRoleSerializer
    queryset = PermissionRole.objects.all()
