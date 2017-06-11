# -*- coding: utf-8 -*-

from rest_framework import serializers

from tandlr.core.api.serializers import ModelSerializer
from tandlr.feedbacks.models import Feedback
from tandlr.scheduled_classes.models import Class
from tandlr.users.serializers import (
    UserShortDetailSerializer,
    UserShortV2Serializer
)


class FeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = Feedback
        fields = (
            'id',
            'feedback',
            'is_feedback_teacher',
            'feedback_to_user',
            'feedback_from_user',
            'feedback_class',
            'score',
            'create_date',
            'feedback_status'
        )


class FeedbackFullSerializer(serializers.ModelSerializer):
    feedback_to_user = UserShortDetailSerializer()
    feedback_from_user = UserShortDetailSerializer()

    class Meta:
        model = Feedback
        fields = (
            'id',
            'feedback',
            'is_feedback_teacher',
            'feedback_to_user',
            'feedback_from_user',
            'feedback_class',
            'score',
            'create_date',
            'feedback_status'
        )


class FeedbackDetailFeedbackFromUserSerializer(serializers.ModelSerializer):
    feedback_from_user = UserShortDetailSerializer()

    class Meta:
        model = Feedback
        fields = (
            'id',
            'feedback',
            'is_feedback_teacher',
            'feedback_to_user',
            'feedback_from_user',
            'feedback_class',
            'score',
            'create_date',
            'feedback_status'
        )


class FeedbackBaseV2Serializer(ModelSerializer):

    class Meta:
        model = Feedback
        fields = (
            'feedback',
            'is_feedback_teacher',
            'feedback_to_user',
            'feedback_from_user',
            'feedback_class',
            'score',
            'create_date',
        )

    def validate(self, data):
        session = Class.objects.get(pk=data['feedback_class'].id)
        from_user = data['feedback_from_user']

        if not (from_user == session.teacher or from_user == session.student):
            raise serializers.ValidationError(
                "The user can only create a feedback to their own sessions."
            )

        return data


class FeedbackDocV2Serializer(ModelSerializer):
    """
    Serializer used to show the documentation with the required fields.
    """

    session = serializers.IntegerField(
        source='feedback_class'
    )

    score = serializers.DecimalField(
        required=True,
        max_digits=3,
        decimal_places=2
    )

    class Meta:
        model = Feedback
        fields = (
            'feedback',
            'score',
            'session',
        )


class FeedbackV2Serializer(FeedbackBaseV2Serializer):

    feedback_to_user = UserShortV2Serializer()
    feedback_from_user = UserShortV2Serializer()

    class Meta:
        model = Feedback
        fields = (
            'feedback',
            'is_feedback_teacher',
            'feedback_to_user',
            'feedback_from_user',
            'feedback_class',
            'score',
            'create_date',
            'feedback_status'
        )
