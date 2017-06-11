# -*- coding: utf-8 -*-
"""
viewsets to manage the chat and chat messages inside tandlr.
"""

from datetime import timedelta

from django.db.models import Q
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response

from tandlr.api.v2.routers import router
from tandlr.chat.models import Chat, Message
from tandlr.chat.permissions import HasTeacherRolePermission
from tandlr.chat.serializers import (
    ChatListV2Serializer,
    ChatV2Serializer,
    MessageBaseV2Serializer,
    MessageListV2Serializer,
    MessageV2Serializer
)
from tandlr.core.api import mixins
from tandlr.core.api.viewsets import GenericViewSet
from tandlr.core.api.viewsets.nested import NestedViewset


class ChatViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        GenericViewSet):

    serializer_class = ChatV2Serializer
    retrieve_serializer_class = ChatListV2Serializer
    list_serializer_class = ChatListV2Serializer

    permission_classes = (HasTeacherRolePermission, )

    def list(self, request, *args, **kwargs):
        """
        Returns a chat list that belongs to the current session's user.
        ---
        response_serializer: ChatListV2Serializer

        responseMessages:
            - code: 200
              message: ok
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(ChatViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Returns the full information about a chat that belongs to the session's
        user.
        ---
        response_serializer: ChatListV2Serializer

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
        return super(ChatViewSet, self).retrieve(request, *args, **kwargs)

    def get_queryset(self):
        role = self.request.query_params.get('role', None)

        #
        # Validates that the session's user is equals to the teacher
        # of the chat. The status of the session should be one of the
        # following:
        #   * Scheduled
        #   * Accepted
        #   * On Course
        #   * Pending
        #
        chats = Chat.objects.filter(
            is_active=True,
            session__class_status__id__in=[2, 3, 4, 5, 6],
            session__class_end_date__gte=(timezone.now() - timedelta(hours=8))
        )

        if role == 'teacher':
            #
            # Validates that the session's user is equals to the teacher of the
            # chat.
            #
            chats = chats.filter(teacher=self.request.user)
        else:
            #
            # Validates that the session's user is equals to the student of the
            # chat.
            #
            chats = chats.filter(student=self.request.user)

        return chats.order_by('session__class_start_date')


class MessagesViewset(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        NestedViewset):

    serializer_class = MessageBaseV2Serializer
    create_serializer_class = MessageV2Serializer
    list_serializer_class = MessageListV2Serializer
    retrieve_serializer_class = MessageListV2Serializer

    parent_model = Chat
    parent_model_name = 'Chat'
    parent_lookup_field = 'pk'

    def create(self, request, *args, **kwargs):
        """
        Allows the current user to create a new message in specific chat.
        ---
        response_serializer: MessageListV2Serializer

        responseMessages:
            - code: 201
              message: CREATED
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        request.data['chat'] = kwargs['chat_pk']
        request.data['sender'] = request.user.id
        return super(MessagesViewset, self).create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Return a message list that belongs to the current user's chat.
        ---
        response_serializer: MessageListV2Serializer

        parameters:
            - name: since
              type: date
              in: query
              description: Start date to get a messages list.
                for example '2016-05-02-14-50-35-998877'

        responseMessages:
            - code: 200
              message: ok
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        try:
            start_date = self.request.query_params.get('since', None)

            if start_date:
                timezone.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%fZ')

        except ValueError:
            return Response(
                {
                    "since": (
                        'since parameter is invalid, or does not have the '
                        'right format "%Y-%m-%dT%H:%M:%S.%fZ".'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super(MessagesViewset, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Returns the full information about a message that belongs to specific
        chat.
        ---
        response_serializer: ChatListV2Serializer

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
        return super(MessagesViewset, self).retrieve(request, *args, **kwargs)

    def get_queryset(self):

        #
        # The messages can only be filtered by date when the action is equals
        # to 'list'.
        #
        start_date = None

        if self.action == 'list' and self.request.query_params.get('since'):
            start_date = timezone.datetime.strptime(
                self.request.query_params.get('since'),
                '%Y-%m-%dT%H:%M:%S.%fZ'
            )

        #
        # The status of the session should be one of the following:
        #   * Scheduled
        #   * Accepted
        #   * On Course
        #   * Pending
        #
        messages = Message.objects.filter(
            Q(
                chat=self.kwargs['chat_pk'],
                chat__session__class_status__id__in=[2, 3, 4, 6],
                is_active=True,
                chat__session__class_end_date__gte=(
                    timezone.now() - timedelta(hours=8)
                )
            ) &
            Q(
                Q(chat__student=self.request.user) |
                Q(chat__teacher=self.request.user)
            )
        )

        if start_date:
            messages = messages.filter(
                created_date__gt=start_date
            )

        return messages.order_by('created_date')


router.register(
    r'chats',
    ChatViewSet,
    base_name='chats'
)

router.register_nested(
    r'chats',
    r'messages',
    MessagesViewset,
    parent_lookup_name='chat',
    base_name='messages'
)
