# -*- coding: utf-8 -*-
from calendar import timegm
from datetime import datetime, timedelta

from django.utils.translation import ugettext as _

import jwt

from rest_framework import serializers

from rest_framework_jwt.compat import Serializer
from rest_framework_jwt.settings import api_settings

from tandlr.registration.models import RegistrationProfile, ResetPassword

from tandlr.users.models import (
    DeviceUser,
    User,
    UserSettings
)

from tandlr.utils.refresh_token import jwt_decode_handler

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class RegistrationProfileSerializer(serializers.ModelSerializer):

    device_user_token = serializers.CharField(
        max_length=250,
        allow_blank=True,
        trim_whitespace=False,
        required=False
    )
    device_os = serializers.CharField(
        max_length=7,
        allow_blank=False,
        trim_whitespace=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'photo',
            'username',
            'email',
            'password',
            'device_os',
            'device_user_token',
            'gender'

        )

        write_only_fields = ('password', 'email', 'username')

    def save(self, request, validated_data):
        """
        Create register in table's user and register.
        """
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data['username'].encode('utf-8'),
            gender=validated_data.get('gender'),
            photo=validated_data.get('photo'),
        )

        # Create device
        try:
            device = DeviceUser.objects.get(user=user)
            device.device_user_token = validated_data.get(
                'device_user_token',
                None
            ),
            device.device_os = validated_data.get('device_os'),
            device.status = True
            device.save()
        except DeviceUser.DoesNotExist:
            DeviceUser(
                user=user,
                device_user_token=validated_data.get(
                    'device_user_token',
                    None
                ),
                device_os=validated_data.get('device_os'),
                is_active=True
            ).save()

        #
        # Sending registration message to new user.
        #
        RegistrationProfile.objects.activation_user(
            user=user,
            request=request
        )

        return user


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
            'available'
        )


class RegistrationResultSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    settings = UserSettingsSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'photo',
            'thumbnail',
            'username',
            'email',
            'is_active',
            'is_student',
            'gender',
            'is_teacher',
            'token',
            'settings',

        )

    def get_token(self, obj):
        """
        Create token to user when user register.
        """

        user = User.objects.get(email=obj.email)

        payload = jwt_payload_handler(user)

        if api_settings.JWT_ALLOW_REFRESH:
            payload['orig_iat'] = timegm(
                datetime.utcnow().utctimetuple()
            )

        token = jwt_encode_handler(payload)

        return token


class NewPasswordSerializer(serializers.ModelSerializer):
    """
    Serializer for reset password.
    """
    email = serializers.CharField(
        max_length=150,
        required=True
    )

    class Meta:
        model = User
        fields = (
            'email',
        )

    def validate_email(self, value):
        """
        Validation email
        """
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("The email does not exist")

        return value

    def create(self, validated_data):
        mail = validated_data.get('email', None)

        user = ResetPassword.objects.reset_user_password(email=mail)
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for change password.
    """
    password = serializers.CharField(
        max_length=150,
        required=True
    )
    token = serializers.CharField(
        max_length=40,
        required=True
    )

    def validate_token(self, value):
        """
        Validation token
        """
        try:
            status = ResetPassword.objects.get(activation_key=value)
        except ResetPassword.DoesNotExist:
            raise serializers.ValidationError("The code does not exist")

        if status.is_activated:
            raise serializers.ValidationError("The code has already been used")
        if status.key_expired:
            raise serializers.ValidationError("The code already expired")
        return value

    def create(self, validated_data):
        """
        Change password
        """
        password = validated_data.get('password', None)
        token = validated_data.get('token', None)
        use_token = ResetPassword.objects.get(activation_key=token)
        use_token.is_activated = True
        use_token.save()
        user = User.objects.get(id=use_token.user.id)
        user.set_password(password)
        user.save()
        return user


class VerificationBaseSerializer(Serializer):
    """
    Abstract serializer used for verifying and refreshing JWTs.
    """
    token = serializers.CharField()

    def validate(self, attrs):
        msg = 'Please define a validate method.'
        raise NotImplementedError(msg)

    def _check_payload(self, token):
        # Check payload valid (based off of JSONWebTokenAuthentication,
        # may want to refactor)
        try:
            payload = jwt_decode_handler(token)
        except jwt.ExpiredSignature:
            msg = _('Signature has expired.')
            raise serializers.ValidationError(msg)
        except jwt.DecodeError:
            msg = _('Error decoding signature.')
            raise serializers.ValidationError(msg)

        return payload

    def _check_user(self, payload):
        username = jwt_get_username_from_payload(payload)

        if not username:
            msg = _('Invalid payload.')
            raise serializers.ValidationError(msg)

        # Make sure user exists
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            msg = _("User doesn't exist.")
            raise serializers.ValidationError(msg)

        if not user.is_active:
            msg = _('User account is disabled.')
            raise serializers.ValidationError(msg)

        return user


class ResetTokenSerializer(VerificationBaseSerializer):
    """
    Refresh an access token.
    """

    def validate(self, attrs):
        token = attrs['token']

        payload = self._check_payload(token=token)
        user = self._check_user(payload=payload)
        # Get and check 'orig_iat'
        orig_iat = payload.get('orig_iat')

        if orig_iat:
            # Verify expiration
            refresh_limit = api_settings.JWT_REFRESH_EXPIRATION_DELTA

            if isinstance(refresh_limit, timedelta):
                refresh_limit = (refresh_limit.days * 24 * 3600 +
                                 refresh_limit.seconds)

            expiration_timestamp = orig_iat + int(refresh_limit)
            now_timestamp = timegm(datetime.utcnow().utctimetuple())

            if now_timestamp > expiration_timestamp:
                msg = _('Refresh has expired.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('orig_iat field is required.')
            raise serializers.ValidationError(msg)

        new_payload = jwt_payload_handler(user)
        new_payload['orig_iat'] = orig_iat

        return {
            'token': jwt_encode_handler(new_payload),
            'user': user
        }


class ChangePasswordV2Serializer(serializers.Serializer):
    """
    Serializer for change password.
    """
    password = serializers.CharField(
        max_length=150,
        required=True
    )
    token = serializers.CharField(
        max_length=40,
        required=True
    )

    def validate_token(self, value):
        """
        Validation token
        """
        try:
            status = ResetPassword.objects.get(activation_key=value)
        except ResetPassword.DoesNotExist:
            raise serializers.ValidationError("The code does not exist")

        if status.is_activated:
            raise serializers.ValidationError("The code has already been used")
        if status.key_expired:
            raise serializers.ValidationError("The code already expired")
        return value

    def create(self, validated_data):
        """
        Change password
        """
        password = validated_data.get('password', None)
        token = validated_data.get('token', None)
        use_token = ResetPassword.objects.get(activation_key=token)
        use_token.is_activated = True
        use_token.save()
        user = User.objects.get(id=use_token.user.id)
        user.set_password(password)
        user.save()
        return user


class NewPasswordV2Serializer(serializers.ModelSerializer):
    """
    Serializer for reset password.
    """
    email = serializers.CharField(
        max_length=150,
        required=True
    )

    class Meta:
        model = User
        fields = (
            'email',
        )

    def validate_email(self, value):
        """
        Validation email
        """
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("The email does not exist")

        return value

    def create(self, validated_data):
        mail = validated_data.get('email', None)
        user = ResetPassword.objects.reset_user_password(
            email=mail,
            request=self.context['request']
        )
        return user


class RegistrationProfileV2Serializer(serializers.ModelSerializer):

    device_user_token = serializers.CharField(
        max_length=250,
        allow_blank=True,
        trim_whitespace=False,
        required=False
    )
    device_os = serializers.CharField(
        max_length=7,
        allow_blank=False,
        trim_whitespace=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'device_os',
            'device_user_token',
            'gender'

        )

        write_only_fields = ('password', 'email', 'username')

    def save(self, request, validated_data):
        """
        Create register in table's user and register.
        """
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data['username'],
            gender=validated_data.get('gender'),
        )

        # Create device

        try:
            device = DeviceUser.objects.get(user=user)
            device.device_user_token = validated_data.get(
                'device_user_token', None),
            device.device_os = validated_data['device_os'],
            device.status = True
            device.save()

        except DeviceUser.DoesNotExist:

            device_user_token = validated_data.get('device_user_token')
            device_os = validated_data.get('device_os')

            if (isinstance(device_user_token, unicode) and
                    len(device_user_token) == 64 and
                    (not device_os or device_os == '')):
                device_os = 'iOS'

            DeviceUser.objects.create(
                user=user,
                device_user_token=device_user_token,
                device_os=device_os,
                is_active=True
            )

            #
            # Sending email to new user.
            #
            RegistrationProfile.objects.activation_user(
                user=user,
                request=request
            )
        return user


class RegistrationResultV2Serializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    settings = UserSettingsSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'thumbnail',
            'username',
            'email',
            'is_active',
            'is_student',
            'gender',
            'is_teacher',
            'token',
            'settings',

        )

    def get_token(self, obj):
        """
        Create token to user when user register.
        """

        user = User.objects.get(email=obj.email)

        payload = jwt_payload_handler(user)

        if api_settings.JWT_ALLOW_REFRESH:
            payload['orig_iat'] = timegm(
                datetime.utcnow().utctimetuple()
            )

        token = jwt_encode_handler(payload)

        return token
