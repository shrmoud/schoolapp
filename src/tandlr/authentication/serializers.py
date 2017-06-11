# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404

from rest_framework import serializers

from tandlr.core.api.serializers import ModelSerializer
from tandlr.users.models import DeviceUser, User, UserSettings
from tandlr.utils.refresh_token import create_token


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        required=True
    )

    password = serializers.CharField(
        required=True
    )

    device_user_token = serializers.CharField(
        max_length=250,
        allow_blank=True,
        required=False
    )

    device_os = serializers.CharField(
        max_length=30,
        allow_blank=False
    )

    def validate(self, data):
        """
        Validation email.
        """
        try:
            user = User.objects.get(email__iexact=data.get('email'))
        except User.DoesNotExist:
            raise serializers.ValidationError("invalid credentials")

        if not user.check_password(data.get('password')):
            raise serializers.ValidationError("invalid credentials")

        return data

    def create(self, validated_data):
        # Valitation mail
        user = get_object_or_404(User, email=validated_data.get('email'))

        device_user_token = validated_data.get('device_user_token')
        device_os = validated_data.get('device_os')

        if (isinstance(device_user_token, unicode) and
                len(device_user_token) == 64 and
                (not device_os or device_os == '')):
            device_os = 'iOS'

        # Save data of the device
        device, created = DeviceUser.objects.get_or_create(
            user=user,
            device_user_token=device_user_token
        )

        device.device_os = device_os
        device.is_active = True
        device.save()

        return user


class LogoutSerializer(ModelSerializer):
    """
    Serializer for log users out.
    """
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = DeviceUser
        fields = ['device_user_token', 'device_os', 'is_active']

    def validate(self, data):
        """
        Validate that the requesting user owns the given device.
        """
        request = self.context['request']
        data.setdefault('user', request.user)
        data.setdefault('device_user_token', None)

        if not request.user.is_authenticated():
            raise serializers.ValidationError('user is not logged in.')

        try:
            self.instance = DeviceUser.objects.get(**data)

        except DeviceUser.DoesNotExist:
            raise serializers.ValidationError('invalid device')

        return data

    def update(self):
        """
        Mark the given device as inactive.
        """
        self.instance.is_active = False
        self.instance.save()

        return self.instance


class UserSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSettings
        fields = (
            'id',
            'session_confirm',
            'message',
            'session_cancellation',
            'location_change',
            'session_reminder',
            'available',
            'push_notifications_enabled'
        )


class UserProfileDetailSerializer(serializers.ModelSerializer):

    token = serializers.SerializerMethodField()
    settings = UserSettingsSerializer()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'name', 'last_name',
            'second_last_name', 'description', 'photo', 'email',
            'phone', 'zip_code', 'birthday', 'gender', 'is_student',
            'is_teacher', 'token', 'settings'
        )

    def get_token(self, obj):
        """
        Create token.
        """
        return create_token(obj)


class LoginResponseV2Serializer(serializers.ModelSerializer):
    """
    Serializer used to return the proper token, when the user was succesfully
    logged in.
    """

    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('token', )

    def get_token(self, obj):
        """
        Create token.
        """
        return create_token(obj)
