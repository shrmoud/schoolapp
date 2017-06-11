# -*- coding: utf-8 -*-
from django.db import models

from tandlr.users.models import User


class Role(models.Model):
    """
    Mapping table role in Tandlr.
    """
    name = models.TextField(
        max_length=45,
        blank=False,
        null=False,
        unique=True,
    )
    description = models.TextField(
        max_length=100,
        blank=True,
        null=True
    )
    status = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = 'role'

    def __unicode__(self):
        return u'{0}'.format(self.name)


class RoleUser(models.Model):
    """
    Mapping role_user table in Tandlr.
    """
    role = models.ForeignKey(
        Role,
        null=False
    )
    user = models.ForeignKey(
        User,
        null=False,
        related_name="roles"
    )

    class Meta:
        db_table = 'role_user'
        unique_together = ("role", "user")


class Permission(models.Model):
    """
    Mapping permission table in Tandlr.
    """
    name = models.TextField(
        max_length=45,
        blank=False,
        null=False,
        unique=True,
    )
    description = models.TextField(
        max_length=100,
        blank=True,
        null=True
    )
    status = models.BooleanField(
        default=True
    )

    def __unicode__(self):
        return u'{0}'.format(self.name)


class PermissionRole(models.Model):
    """
    Mapping permission_role table in Tandlr.
    """
    permission = models.ForeignKey(
        Permission,
        null=False
    )
    role = models.ForeignKey(
        Role,
        null=False,
        related_name="permission"
    )

    class Meta:
        db_table = 'permission_role'
        unique_together = ("permission", "role")
