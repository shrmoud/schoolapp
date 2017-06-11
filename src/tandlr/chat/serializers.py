# -*- coding: utf-8 -*-

from django.template.loader import render_to_string

from rest_framework import serializers

from tandlr.chat.models import Chat, Message
from tandlr.core.api.serializers import ModelSerializer
from tandlr.notifications.models import Notification
from tandlr.scheduled_classes.serializers import SessionListV2Serializer
from tandlr.users.serializers import UserShortV2Serializer


class ChatV2Serializer(ModelSerializer):
    class Meta:
        model = Chat
        fields = (
            'id',
            'teacher',
            'student',
            'session',
            'created_date'
        )


class ChatListV2Serializer(ChatV2Serializer):
    teacher = UserShortV2Serializer()
    student = UserShortV2Serializer()
    session = SessionListV2Serializer()

    class Meta:
        model = Chat
        fields = (
            'id',
            'teacher',
            'student',
            'session',
            'created_date'
        )


class MessageBaseV2Serializer(ModelSerializer):
    class Meta:
        model = Message
        fields = (
            'id',
            'message'
        )


class MessageV2Serializer(MessageBaseV2Serializer):

    class Meta:
        model = Message
        fields = (
            'id',
            'sender',
            'chat',
            'message'
        )

    def validate_sender(self, sender):
        request = self.context['request']
        if request.user != sender:
            raise serializers.ValidationError(
                "The sender should be equals to session's user."
            )

        return sender

    def validate_chat(self, chat):
        request = self.context['request']
        if not (request.user == chat.teacher or request.user == chat.student):
            raise serializers.ValidationError(
                "The user can only create a message to their own chats."
            )

        return chat

    def create(self, validated_data):
        message = Message(**validated_data)
        message.save()

        if message.sender == message.chat.teacher:
            receiver = message.chat.student
        else:
            receiver = message.chat.teacher

        context = {'message': message}
        subject_template = 'email/chat/chat_new_message.txt'
        subject = render_to_string(subject_template, context).strip()

        Notification.objects.create(
            receiver=receiver,
            sender=message.sender,
            target_action='new_message',
            target=message.chat,
            body=subject
        )

        return message


class MessageListV2Serializer(MessageV2Serializer):
    sender = UserShortV2Serializer()

    class Meta:
        model = Message
        fields = (
            'id',
            'sender',
            'message',
            'created_date'
        )
