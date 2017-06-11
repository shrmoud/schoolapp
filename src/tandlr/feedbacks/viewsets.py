# -*- coding: utf-8 -*-
from rest_framework import filters
from rest_framework import viewsets

from tandlr.feedbacks.models import Feedback

from tandlr.feedbacks.serializers import (
    FeedbackFullSerializer,
    FeedbackSerializer,
    UserShortDetailSerializer
)

from tandlr.users.models import User


class FeedbackViewSet(viewsets.ModelViewSet):
    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()


class FeedbackFullViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Filter to feedback registers
    ---
    - You can filter by all fields.
    ---
    - You can search only by feedback field.
    ---
    - You can ordering by all field's, example : ordering=id,-score
    ---
    - page_size (example : /?page_size=10)
    ---
    ---
    """
    serializer_class = FeedbackFullSerializer
    queryset = Feedback.objects.all()
    filter_backends = (filters.DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter,)
    search_fields = (
        'feedback'
    )
    ordering_fields = '__all__'
    filter_fields = (
        'id',
        'feedback',
        'is_feedback_teacher',
        'feedback_to_user__id',
        'feedback_from_user__id',
        'score',
        'create_date',
        'feedback_status'
    )


class FeedbackDetailRatesByTeacherViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = UserShortDetailSerializer
    queryset = User.objects.filter(
        is_teacher=True
    ).order_by(
        'user_summary__score_average_teacher'
    )


class FeedbackDetailRatesByStudentViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = UserShortDetailSerializer
    queryset = User.objects.filter(
        is_student=True
    ).order_by(
        'user_summary__score_average_student'
    )
