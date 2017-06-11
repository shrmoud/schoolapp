# -*- coding: utf-8 -*-
import functools

import json

import jwt

from django.contrib.auth import get_user_model  # noqa

from rest_framework_jwt.settings import api_settings

from channels.sessions import channel_session  # noqa

User = get_user_model()
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


def http_jwt_session_user(func):

    @channel_session
    @functools.wraps(func)
    def decorator(message, *args, **kwargs):
        content = json.loads(message.content['text'])
        token = content['jwt'] if 'jwt' in content else None
        # Check payload valid (based off of JSONWebTokenAuthentication,
        # may want to refactor)
        try:
            payload = jwt_decode_handler(token)
        except jwt.ExpiredSignature:
            return 'Signature has expired.'
        except jwt.DecodeError:
            return 'Error decoding signature.'

        username = jwt_get_username_from_payload(payload)

        if not username:
            return 'Invalid payload.'

        # Make sure user exists
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            return "User doesn't exist."

        if not user.is_active:
            return 'User account is disabled.'

        message.user = user

        return func(message, *args, **kwargs)

    return decorator
