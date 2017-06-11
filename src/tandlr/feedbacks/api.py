# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404

from tandlr.api.v2.routers import router
from tandlr.core.api import mixins
from tandlr.core.api.viewsets import GenericViewSet
from tandlr.feedbacks.models import Feedback
from tandlr.feedbacks.serializers import (
    FeedbackBaseV2Serializer,
    FeedbackDocV2Serializer,
    FeedbackV2Serializer
)
from tandlr.scheduled_classes.models import Class
from tandlr.scheduled_classes.serializers import SessionListV2Serializer


class FeedbackViewSet(
        mixins.CreateModelMixin,
        GenericViewSet):

    queryset = Feedback.objects.all()
    serializer_class = FeedbackDocV2Serializer
    create_serializer_class = FeedbackBaseV2Serializer
    retrieve_serializer_class = FeedbackV2Serializer

    def create(self, request, *args, **kwargs):
        """
        Allows the current user to create a new session feedback.
        ---
        request_serializer: FeedbackDocV2Serializer
        response_serializer: FeedbackV2Serializer

        responseMessages:
            - code: 201
              message: CREATED
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        session = get_object_or_404(Class, pk=request.data['session'])
        request.data['is_feedback_teacher'] = request.user != session.teacher
        request.data['feedback_class'] = session.id

        if request.data['is_feedback_teacher']:
            request.data['feedback_from_user'] = request.user.id
            request.data['feedback_to_user'] = session.teacher.id
        else:
            request.data['feedback_from_user'] = request.user.id
            request.data['feedback_to_user'] = session.student.id

        return super(FeedbackViewSet, self).create(request, *args, **kwargs)


class PendingFeedbackViewset(
        mixins.ListModelMixin,
        GenericViewSet):

    serializer_class = SessionListV2Serializer
    list_serializer_class = SessionListV2Serializer

    def list(self, request, *args, **kwargs):
        """
        Returns the session's pending feedbacks.
        ---
        response_serializer: SessionListV2Serializer

        parameters:
            - name: role
              type: boolean
              required: false
              in: query

        responseMessages:
            - code: 200
              message: OK
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(
            PendingFeedbackViewset, self).list(request, *args, **kwargs)

    def get_queryset(self):
        role = self.request.query_params.get('role', 'student')

        sessions_taken_ids = Feedback.objects.filter(
            feedback_from_user=self.request.user
        ).values('feedback_class')

        #
        # Exclude the sessions that have been rated and filter only the ended
        # sessions.
        #
        queryset = Class.objects.exclude(id__in=sessions_taken_ids).filter(
            class_status=5
        )

        if role == 'teacher':
            queryset = queryset.filter(teacher=self.request.user)
        else:
            queryset = queryset.filter(student=self.request.user)

        return queryset


router.register(
    'feedbacks/pendings',
    PendingFeedbackViewset,
    'feedbacks/pendings'
)

router.register(
    'feedbacks',
    FeedbackViewSet,
    base_name='feedbacks'
)
