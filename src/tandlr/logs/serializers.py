# -*- coding: utf-8 -*-
from rest_framework import serializers

from tandlr.logs.models import (
    LogMail,
    LogbookUser
)


class LogbookUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = LogbookUser
        fields = (
            'id',
            'activity',
            'module',
            'body_log',
            'log_level',
            'logbook_date'
        )


class LogMailSerializer(serializers.ModelSerializer):

    class Meta:
        model = LogMail
        fields = (
            'id',
            'mail_from',
            'mail_subject',
            'mail_sent_date'
        )
