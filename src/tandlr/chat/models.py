# -*- coding: utf-8 -*-
"""
Define functionality of the chats inside tandlr.
"""
from datetime import timedelta

from django.db import models

from tandlr.core.db.models.models import TimeStampedMixin
from tandlr.scheduled_classes.models import Class
from tandlr.users.models import User


class Chat(TimeStampedMixin):
    """
    Teachers and students can send messages between them.

    A user that acts as teacher can send or receiver chats from a user that
    acts as student. The period of chat life is since that the teacher accept a
    session until one day before of the session.

    Attributes:
        teacher (int): The user that acts as teacher in the session.
        student (int): The user that acts as student in the session.
        session (int): The session to wich belongs this conversation.
        chat_status (boolean): Tells whether this conversation is active or
            inactive.
    """

    teacher = models.ForeignKey(
        User,
        null=False,
        related_name="chat_teacher"
    )

    student = models.ForeignKey(
        User,
        null=False,
        related_name="chat_student"
    )

    session = models.OneToOneField(
        Class,
        null=False,
        on_delete=models.CASCADE,
        related_name="chat_session"
    )

    is_active = models.BooleanField(
        default=True
    )

    @property
    def expiration_date(self):
        """
        Return the chat expiration date.
        """
        if self.session.class_end_date:
            return self.session.class_end_date + timedelta(days=1)

        elif self.session.class_start_date:
            expiration_date = self.session.class_start_date + timedelta(days=1)

            self.session.class_end_date = expiration_date
            self.session.save()
            return expiration_date

        else:
            return None

    def __unicode__(self):
        """
        Return the full names of the teacher and student.
        """
        return u'{0} - {1}'.format(
            self.teacher.get_full_name(),
            self.student.get_full_name()
        )


class Message(TimeStampedMixin):
    """
    Represents a message in a conversation in Tandlr.

    The messages that are sent belongs only a chat, and the chat belongs to
    a session. The messages are hidden between sessions although are belongs
    the same users.

    Attributes:
        sender (int): The user who sent the message.
        chat (int): Conversation to wich belongs the message.
        message (str): The message body.
        chat_reply_status (boolean): Tells whether the message was delivered
            or not
    """

    sender = models.ForeignKey(
        User,
        null=False
    )

    chat = models.ForeignKey(
        Chat,
        null=False
    )

    message = models.TextField(
        max_length=500,
        blank=False,
        null=False
    )

    is_active = models.BooleanField(
        default=True
    )

    def __unicode__(self):
        """
        Return the sender full name and the message body.
        """
        return self.message
