# -*- coding: utf-8 -*-
from datetime import time
from decimal import Decimal

from django.conf import settings
from django.contrib.gis.db import models as gismodels
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _

from tandlr.balances.models import Balance
from tandlr.catalogues.models import University
from tandlr.promotions.models import PromotionCode
from tandlr.users.models import User


class Subject(models.Model):
    """
    Mappin table subject in Tandlr.
    """
    name = models.CharField(
        max_length=45,
        blank=False,
        null=False,
        unique=True
    )
    description = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    status = models.BooleanField(
        default=True
    )
    price_per_hour = models.DecimalField(
        default=settings.DEFAULT_CLASS_PRICE_PER_HOUR,
        max_digits=10,
        decimal_places=2,
        null=False
    )
    university = models.ForeignKey(
        University,
        related_name='subjects'
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'subject'
        verbose_name = "subject"
        verbose_name_plural = "subjects"


class SubjectTeacher(models.Model):
    """
    Mapping table subject_teacher in Tandlr
    """
    teacher = models.ForeignKey(
        User,
        null=False,
        related_name='subject_teacher'
    )
    subject = models.ForeignKey(
        Subject,
        null=False,
        related_name='subjects'
    )
    status = models.BooleanField(
        default=True
    )

    def __unicode(self):
        return u'{0} - {1}'.format(self.teacher.get_full_name(), self.subject)

    class Meta:
        db_table = 'subject_teacher'
        unique_together = ("teacher", "subject")
        verbose_name = "teacher subject"
        verbose_name_plural = "teacher subjects"


class ClassStatus(models.Model):
    """
    Mapping class_status in Tandlr.
    """
    name = models.CharField(
        max_length=45,
        blank=False,
        null=False,
        unique=True
    )

    description = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    status = models.BooleanField(
        default=True
    )

    order = models.PositiveIntegerField(
        blank=False,
        null=False,
        default=1,
        help_text=_(
            "Defines the order how to will display the list class"
        )
    )

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'class_status'
        verbose_name_plural = u'class status'


class Class(models.Model):
    """
    Mapping table class in Tandlr.
    """
    teacher = models.ForeignKey(
        User,
        null=False,
        related_name="class_teacher"
    )

    student = models.ForeignKey(
        User,
        null=False,
        related_name="class_student"
    )

    subject = models.ForeignKey(
        Subject,
        null=False,
        related_name='class_subject'
    )

    class_start_date = models.DateTimeField()

    class_time = models.TimeField()

    class_end_date = models.DateTimeField()

    class_status = models.ForeignKey(
        ClassStatus,
        null=False,
        related_name='class_status'
    )

    class_detail = models.TextField(
        max_length=500,
        blank=True,
        null=True
    )

    location = gismodels.PointField(srid=4326)

    time_zone_conf = models.IntegerField()

    participants = models.PositiveIntegerField(
        blank=False,
        null=False,
        validators=[
            validators.MinValueValidator(1)
        ],
        help_text=_('Defines the students number that will be in the session')
    )

    place_description = models.TextField(
        max_length=250,
        blank=True,
        null=True
    )

    promo_code = models.ForeignKey(
        PromotionCode,
        blank=True,
        null=True,
        related_name='session',
        verbose_name='promotion code'
    )

    meeting_now = models.BooleanField(
        default=False,
        verbose_name='meeting now'
    )

    objects = gismodels.GeoManager()

    class Meta:
        db_table = 'class'
        verbose_name = 'session'
        verbose_name_plural = 'sessions'

    def __unicode__(self):
        return u'{0} - {1}'.format(
            self.subject.name,
            self.teacher.get_full_name()
        )

    @property
    def student_feedback(self):
        """
        If exists, this property returns the feedback given by student.
        """
        try:
            return self.feedbacks.get(
                feedback_from_user=self.student,
                is_feedback_teacher=False
            ).score
        except self.feedbacks.model.DoesNotExist:
            return None

    @property
    def teacher_feedback(self):
        """
        If exists, this property returns the feedback given by teacher.
        """
        try:
            return self.feedbacks.get(
                feedback_from_user=self.teacher,
                is_feedback_teacher=True
            ).score
        except self.feedbacks.model.DoesNotExist:
            return None


class ClassBill(models.Model):

    promo_code = models.ForeignKey(
        PromotionCode,
        blank=True,
        null=True,
        related_name='class_bills',
        verbose_name='promotion code'
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Created date"
    )

    hourly_price = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        default=Decimal('0.00'),
        verbose_name='hourly price'
    )

    number_of_hours = models.TimeField(
        default=time(hour=0, minute=0),
        verbose_name='number of hours'
    )

    subtotal = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        default=Decimal('0.00'),
        verbose_name='subtotal'
    )

    commission = models.PositiveIntegerField(
        default=0,
        verbose_name='commission'
    )

    commission_amount = models.DecimalField(
        decimal_places=2,
        max_digits=6,
        default=Decimal('0.00'),
        verbose_name='commission amount'
    )

    session = models.ForeignKey(
        'Class',
        blank=True,
        null=True,
        related_name='bills',
        verbose_name='session'
    )

    was_paid = models.BooleanField(
        default=False,
        verbose_name='was paid'
    )

    balance = models.ForeignKey(
        Balance,
        blank=True,
        null=True,
        related_name='bills',
        verbose_name='balance'
    )

    charge_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='charge id'
    )

    @property
    def total_hours(self):
        """
        return the total hours of this classbills in format HH:MM
        """
        return self.number_of_hours.strftime("%H:%M")

    @property
    def student(self):
        return self.session.student

    @property
    def teacher(self):
        return self.session.teacher

    @property
    def student_total(self):
        return self.subtotal * ( 1 - (self.promo_code.discount / 100))

    @property
    def teacher_total(self):
        return self.subtotal - self.commission_amount

    @property
    def duration(self):
        number_of_hours_format = self.number_of_hours.strftime('%H:%M')
        return number_of_hours_format


class RequestClassExtensionTime(models.Model):
    """
    Mapping table request class extension time in Tandlr.
    """

    class_request = models.ForeignKey(
        Class,
        null=False,
        related_name="extensions_time_class"
    )
    time = models.TimeField(
        null=False
    )
    accepted = models.BooleanField(
        default=False
    )
    finished = models.BooleanField(
        default=False
    )
    extension_time_end_date = models.DateTimeField(
        null=True
    )

    class Meta:
        db_table = 'request_class_extension_time'

    def __unicode__(self):
        return u'{0} - {1} - {2}'.format(
            self.class_request.teacher,
            self.class_request.student,
            self.class_request.subject
        )


class Slot(models.Model):
    teacher = models.ForeignKey(
        User,
        null=False,
        related_name='availability_slots'
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_unique = models.BooleanField(default=False)

    # Only if is an unique slot.
    date = models.DateField(
        null=True,
        blank=True
    )

    # Only if is not an unique slot.
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    thursday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
    sunday = models.BooleanField(default=False)

    def __unicode__(self):

        days = [
                'monday',
                'tuesday',
                'wednesday',
                'thursday',
                'friday',
                'saturday',
                'sunday'
        ]
        start_time_format = self.start_time.strftime("%H:%M")
        end_time_format = self.end_time.strftime("%H:%M")

        if self.is_unique:
            return '{} is Available {}, from {} to {}'. format(
                self.teacher.email,
                self.date,
                start_time_format,
                end_time_format
            )
        else:
            teacher_availability="{} is Available: ".format(
                self.teacher.email,
            )

            for day in days:
                if getattr(self, day):
                    available_day = '{}, '.format(
                        day
                    )
                    teacher_availability += available_day
            teacher_availability += "from {} to {}".format(
                start_time_format,
                end_time_format
            )
            return teacher_availability

