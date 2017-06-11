# -*- coding: utf-8 -*-
from django.conf import settings

from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from tandlr.scheduled_classes.models import Class
from tandlr.users.models import User
from tandlr.users.models import UserSummary


class Feedback(models.Model):
    """
    Mapping table feedback between students and teachers in Tandlr.
    """
    feedback = models.TextField(
        max_length=500,
        blank=False,
        null=False
    )

    feedback_status = models.BooleanField(
        default=True
    )

    is_feedback_teacher = models.BooleanField(
        default=False,
        verbose_name=u'Is teacher feedback'
    )
    create_date = models.DateField(
        auto_now=True
    )
    feedback_to_user = models.ForeignKey(
        User,
        null=False,
        related_name='feedback_to_user'
    )
    feedback_from_user = models.ForeignKey(
        User,
        null=False,
        related_name='feedback_from_user'
    )
    feedback_class = models.ForeignKey(
        Class,
        null=False,
        related_name='feedbacks'
    )
    score = models.FloatField(
        default=0.0,
        null=True
    )

    def __unicode__(self):
        return u'{0} - {1}'.format(
            self.feedback_from_user.get_full_name(),
            self.feedback_to_user.get_full_name()
        )

    class Meta:
        db_table = 'feedback'


@receiver(post_save, sender=Feedback)
def calculate_user_sumary(sender, instance, **kwargs):
    # Getting the user that was rated in the feedback.
    user = instance.feedback_to_user

    user_summary, created = UserSummary.objects.get_or_create(
        user=user
    )

    valid_feedback_objects = Feedback.objects.filter(
        feedback_status=True,
        is_feedback_teacher=instance.is_feedback_teacher,
        feedback_to_user__id=user.id,
        score__gt=settings.FEEDBACK_MINIMUN_SCORE
    )

    sum_score = valid_feedback_objects.aggregate(
        sum_score=Sum('score'),
    )['sum_score']

    if not sum_score:
        average = 5

    else:
        average = (sum_score + 5) / (len(valid_feedback_objects) + 1)

    if instance.is_feedback_teacher:
        user_summary.score_average_teacher = average
    else:
        user_summary.score_average_student = average

    user_summary.save()
