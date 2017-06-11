# -*- coding: utf-8 -*-
from django.utils import timezone

from rest_framework import decorators, viewsets
from rest_framework.response import Response

from . import serializers
from .models import Notification


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.NotificationSerializer

    @decorators.list_route(methods=['post'])
    def mark_all_as_read(self, request):
        """
        Marks all unread notifications as read.
        ---

        omit_serializer: true

        type:
            updated_items:
                type: int
                required: true

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
        notifications = self.get_queryset()
        count = notifications.filter(is_read=False).update(
            is_read=True,
            last_modified=timezone.now()
        )

        return Response({'updated_items': count})

    @decorators.detail_route(methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Marks the given notification as read.
        ---

        response_serializer: serializers.NotificationSerializer

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
        notification = self.get_object()
        notification.is_read = True
        notification.save()

        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    def get_queryset(self):
        """
        Returns the queryset that will be used to display notifications.

        Only notifications for the current user are included.
        """
        return Notification.objects.filter(
            receiver=self.request.user).order_by('-created_date')
