# -*- coding: utf-8 -*-
from tandlr.core.api.serializers.base import ModelSerializer

from .models import University


class UniversityV2Serializers(ModelSerializer):
    class Meta:
        model = University
        fields = ('id', 'name', 'initial')
