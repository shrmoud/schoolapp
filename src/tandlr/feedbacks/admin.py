# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Feedback


class AdminFeedback(admin.ModelAdmin):
    list_display = [
        'to_user',
        'from_user',
        'feedback_status',
        'is_feedback_teacher',
        'score',
        'create_date',
    ]

    search_fields = [
        'feedback_to_user__name',
        'feedback_to_user__last_name',
        'feedback_to_user__second_last_name',
        'feedback_from_user__name',
        'feedback_from_user__last_name',
        'feedback_from_user__second_last_name',
    ]

    list_filter = [
        'is_feedback_teacher',
    ]

    raw_id_fields = (
        'feedback_to_user',
        'feedback_from_user',
        'feedback_class'
    )

    def to_user(self, instance):
        return instance.feedback_to_user.get_full_name()

    def from_user(self, instance):
        return instance.feedback_from_user.get_full_name()

admin.site.register(Feedback, AdminFeedback)
