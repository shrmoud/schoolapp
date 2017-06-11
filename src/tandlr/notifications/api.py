# -*- coding: utf-8 -*-
import json

from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from tandlr.api.v2.routers import router
from tandlr.core.api import mixins, viewsets

from .models import Notification
from .serializers import NotificationV2Serializer


class NotificationViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):

    serializer_class = NotificationV2Serializer
    list_serializer_class = NotificationV2Serializer
    retrieve_serializer_class = NotificationV2Serializer

    @list_route(methods=['post'])
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

    @detail_route(methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Marks the given notification as read.
        ---

        response_serializer: NotificationV2Serializer

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

    def retrieve(self, request, *args, **kwargs):
        """
        Returns a notification object for the given session's user and id.
        ---
        response_serializer: NotificationV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(NotificationViewSet, self).retrieve(
            request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Returns a list of notifications for the given session's user.
        ---
        response_serializer: NotificationV2Serializer

        parameters:
            - name: read
              type: boolean
              in: query
              description: Filter the notifications by is read.
                For example ?read=true

        responseMessages:
            - code: 200
              message: OK
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        try:
            if 'read' in self.request.query_params:
                json.loads(request.query_params.get('read'))
        except Exception:
            return Response(
                {
                    "read": (
                        'read parameter is not valid, should be true or false'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super(NotificationViewSet, self).list(
            request, *args, **kwargs)

    def get_queryset(self):
        """
        Returns the queryset that will be used to display notifications.

        Only notifications for the current user are included.
        """

        queryset = Notification.objects.filter(receiver=self.request.user)

        #
        # Filter by status only when the user sent the 'read' param.
        #
        if 'read' in self.request.query_params:
            as_read = json.loads(self.request.query_params.get('read', None))

            queryset = queryset.filter(is_read=as_read)

        return queryset.order_by('-created_date')

router.register(
    r'me/notifications',
    NotificationViewSet,
    base_name='notifications'
)
