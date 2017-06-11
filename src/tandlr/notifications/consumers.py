# -*- coding: utf-8 -*-
import logging

from channels import Group
from channels.auth import http_session_user
from channels.sessions import channel_session

from tandlr.notifications.decorators import http_jwt_session_user

log = logging.getLogger(__name__)


@channel_session
def ws_connect(message):
        #
        # Add the current user in a group where will be sent the mass
        # notifications without university
        #
        Group('mass-notifications').add(message.reply_channel)


@http_jwt_session_user
def ws_receive(message):
    #
    # Event that listen when a user do login. When this event is triggered,
    # we register the user in his groups.
    #
    if message.user:
        user = message.user
        #
        # Add the current user in its group
        #
        Group('notifications' + str(user.id)).add(message.reply_channel)

        if hasattr(user, 'university_id'):
            #
            # Add the current user in the group of mass notifications to a
            # specific university.
            #
            Group('mass-notifications' + str(user.university_id)).add(
                message.reply_channel
            )


@http_session_user
def ws_disconnect(message):
    if message.user:
        user = message.user
        #
        # Event that listen when a user was disconnect.
        #
        Group('notifications' + str(message.user.id)).discard(
            message.reply_channel
        )

        #
        # Remove user of general mass notifications group.
        #
        Group('mass-notifications').discard(message.reply_channel)

        if hasattr(user, 'university_id'):
            #
            # Remove the user from mass notifications group.
            #
            Group('mass-notifications' + str(user.university_id)).discard(
                message.reply_channel
            )
