# -*- coding: utf-8 -*-
from rest_framework import viewsets

from tandlr.logs.models import (
    LogMail,
    LogbookUser
)
from tandlr.logs.serializers import (
    LogMailSerializer,
    LogbookUserSerializer
)


class LogbookUserViewSet(viewsets.ModelViewSet):
    serializer_class = LogbookUserSerializer
    queryset = LogbookUser.objects.all()


class LogMailViewSet(viewsets.ModelViewSet):
    serializer_class = LogMailSerializer
    queryset = LogMail.objects.all()
