# -*- coding: utf-8 -*-
from rest_framework import serializers
from rest_framework.reverse import NoReverseMatch, reverse

from tandlr.core.api.serializers import ModelSerializer
from tandlr.users.serializers import UserSerializer

from .models import Notification


class NotificationTargetSerializer(serializers.Serializer):
    """
    Custom serializer for the 'target' attribute of the
    ```tandlr.notifications.models.Notification``` model.
    """
    id = serializers.IntegerField(source='target_id')
    type = serializers.CharField(source='target._meta.model_name')
    action = serializers.CharField(source='target_action')
    resource_uri = serializers.SerializerMethodField()

    def get_action(self, obj):
        return 'created'

    def get_resource_uri(self, obj):
        """
        Tries to return the resource uri for the given object if a proper
        viewset is registered in the API. Otherwise returns None.
        """
        url_name = 'api:v1:{0}-detail'.format(obj.target._meta.model_name)

        try:
            return reverse(
                url_name,
                args=[obj.target_id],
                request=self.context.get('request', None)
            )
        except NoReverseMatch:
            return None


class NotificationSerializer(ModelSerializer):
    """
    Serializer class for the ```tandlr.notifications.models.Notification```
    model.
    """
    sender = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'body', 'sender', 'target', 'was_delivered',
            'is_read', 'created_date', 'last_modified'
        ]

    def get_sender(self, obj):
        """
        Returns the notification's sender serialized with the minimal
        required fields.
        """
        if obj.sender:
            serializer = UserSerializer(
                obj.sender,
                context=self.context,
                fields=[
                    'id', 'username', 'email', 'name', 'last_name',
                    'second_last_name', 'photo'
                ]
            )

            return serializer.data

    def get_target(self, obj):
        """
        Returns the notification's target serialized with the minimal
        required fields.
        """
        if obj.target:
            serializer = NotificationTargetSerializer(
                obj, context=self.context)

            return serializer.data


class NotificationV2Serializer(ModelSerializer):
    """
    Serializer class for the ```tandlr.notifications.models.Notification```
    model.
    """
    sender = serializers.SerializerMethodField()
    target = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = [
            'id', 'body', 'sender', 'target', 'was_delivered',
            'is_read', 'created_date', 'last_modified'
        ]

    def get_sender(self, obj):
        """
        Returns the notification's sender serialized with the minimal
        required fields.
        """
        if obj.sender:
            serializer = UserSerializer(
                obj.sender,
                context=self.context,
                fields=[
                    'id', 'username', 'email', 'name', 'last_name',
                    'second_last_name', 'photo', 'thumbnail'
                ]
            )

            return serializer.data

    def get_target(self, obj):
        """
        Returns the notification's target serialized with the minimal
        required fields.
        """
        if obj.target:
            serializer = NotificationTargetSerializer(
                obj, context=self.context
            )

            return serializer.data
