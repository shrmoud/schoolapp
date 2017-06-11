# -*- coding: utf-8 -*-
from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    """
    Allows access only to Studen users.
    """
    def has_permission(self, request, view):
        try:
            return request.user and request.user.is_student
        except AttributeError:
            return False


class IsTeacher(BasePermission):
    """
    Allows access only to teachers users.
    """
    def has_permission(self, request, view):
        try:
            return request.user and request.user.is_teacher
        except AttributeError:
            return False
