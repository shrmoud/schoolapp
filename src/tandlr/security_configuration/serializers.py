# -*- coding: utf-8 -*-
from rest_framework import serializers

from tandlr.security_configuration.models import (
    Permission,
    PermissionRole,
    Role,
    RoleUser
)

from tandlr.users.serializers import UserShortDetailSerializer


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = (
            'id',
            'name',
            'description',
            'status'
        )


class RoleUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = RoleUser
        fields = (
            'id',
            'role',
            'user'
        )


class RoleUserDetailSerializer(serializers.ModelSerializer):

    role = RoleSerializer()
    user = UserShortDetailSerializer()

    class Meta:
        model = RoleUser
        fields = (
            'id',
            'role',
            'user'
        )


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = (
            'id',
            'name',
            'description',
            'status'
        )


class PermissionRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = PermissionRole
        fields = (
            'id',
            'permission',
            'role'
        )


class PermissionRoleDetailSerializer(serializers.ModelSerializer):

    permission = PermissionSerializer()
    role = RoleSerializer()

    class Meta:
        model = PermissionRole
        fields = (
            'id',
            'permission',
            'role'
        )
