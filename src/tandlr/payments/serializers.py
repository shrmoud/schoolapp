# -*- coding: utf-8 -*-
from rest_framework import serializers

from tandlr.payments.models import TeacherPaymentInformation


class TeacherPaymentInformationV2Serializer(serializers.ModelSerializer):

    tutor = serializers.SerializerMethodField()

    class Meta:
        model = TeacherPaymentInformation
        fields = (
            'tutor',
            'bank',
            'account_number',
            'social_security_number',
        )

    def get_tutor(self, instance):

        return instance.teacher.get_full_name()
