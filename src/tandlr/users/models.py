# -*- coding: utf-8 -*-
import os
from hashlib import md5

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.contrib.gis.db import models
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from tandlr.catalogues.models import University
from tandlr.core.db.models import TimeStampedMixin


class UserManager(BaseUserManager):
    """
    Custom manager for create users staff and superuser.
    """
    def _create_user(self, email, password, **extra_fields):
        """
        Method for create new users.
        """
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            last_login=timezone.now(),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Creating new user staff.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_teacher', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creating new user superuser.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


def upload_to_image(instance, filename):
    """
    Get the upload path to the profile image.
    """
    return '{0}/{1}{2}'.format(
        "users/profile_images",
        md5(filename).hexdigest(),
        os.path.splitext(filename)[-1]
    )


def get_user_thumbnail_path(instance, filename):
    """
    Get the proper upload path to the thumbnail profile image.
    """
    return '{0}/{1}'.format(
        "users/profile_images",
        filename
    )


class User(AbstractBaseUser, PermissionsMixin):
    """
    Mapping table user Tandlr.
    """
    gender_choices = (
        (1, 'Female'),
        (2, 'Male'),
        (3, "Don't Specify")
    )

    username = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        unique=True
    )

    name = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    last_name = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    second_last_name = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    description = models.TextField(
        max_length=250,
        blank=True,
        null=True
    )

    photo = models.ImageField(
        null=True,
        blank=True,
        upload_to=upload_to_image
    )

    thumbnail = models.ImageField(
        null=True,
        blank=True,
        upload_to=get_user_thumbnail_path
    )

    email = models.EmailField(
        max_length=50,
        unique=True,
        null=False
    )

    phone = models.TextField(
        max_length=20,
        blank=True,
        null=True
    )

    birthday = models.DateField(
        null=True
    )

    gender = models.IntegerField(
        blank=True,
        null=True,
        choices=gender_choices
    )

    university = models.ForeignKey(
        University,
        blank=True,
        null=True
    )

    zip_code = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    register_date = models.DateField(
        auto_now=True,
    )

    last_modify_date = models.DateField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('is_active')
    )

    is_teacher = models.BooleanField(
        default=False,
        verbose_name=_('is_teacher')
    )

    is_student = models.BooleanField(
        default=True,
        verbose_name=_('is_student')
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name=_('is_staff')
    )

    is_confirmation_email = models.BooleanField(
        default=False
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    @property
    def customer_id(self):
        from tandlr.stripe.models import StripeCustomer
        try:
            return StripeCustomer.objects.get(
                user=self
            )
        except StripeCustomer.DoesNotExist:
            return None

    @property
    def sessions_as_student(self):
        return self.user_summary.lessons_as_student

    @property
    def sessions_as_teacher(self):
        return self.user_summary.sessions_as_teacher

    def price_per_hour(self, subject_id):
        from tandlr.scheduled_classes.models import Subject
        try:
            if self.is_teacher:
                return Subject.objects.get(
                    id=subject_id
                ).price_per_hour

            return None
        except Subject.DoesNotExist:
            return None

    def get_sessions_as_a_teacher(self):
        count_class = self.class_teacher.filter(
            class_status__id=5  # Ended.
        ).count()

        return count_class

    def get_sessions_as_a_student(self):
        count_class = self.class_student.filter(
            class_status__id=5  # Ended.
        ).count()

        return count_class

    def get_rating_as_a_teacher(self):
        return round(self.user_summary.score_average_teacher, 2)

    def get_rating_as_a_student(self):
        return round(self.user_summary.score_average_student, 2)

    class Meta:
        db_table = 'user'

    def __unicode__(self):
        return self.get_full_name()

    def get_full_name(self):
        """
        Return full name user:
             name last_name second_last_name
        """
        parts = [self.name, self.last_name, self.second_last_name]
        return ' '.join(filter(None, parts))

    def get_short_name(self):
        """
        Return short name user:
            name last_name
        """
        return self.name

    def email_user(self, subject, body, html=None, from_email=None, **kwargs):
        """
        Send an email to this user.

            Args:
                subject (str): The subject for the email message.
                body (str): Body for the email message. Must be plain txt.
                html (optional[str]): HTML formatted version of the body.
                    If provided, this version shall be appended to message as
                    an alternative. Defaults to None.
                from_email (optional[str]): Email address that shall be used
                    as the sender of the email message. If it is not provided,
                    then the message will be marked as sent from the address
                    specified in the ```DEFAULT_FROM_EMAIL``` setting.
                    Defaults to None.
                **kwargs: Arbitrary keyword arguments that shall be used to
                    instantiate the ```EmailMultiAlternatives``` class.

            Returns:
                bool: True if the message was successfully sent.
        """
        if not from_email and settings.DEFAULT_FROM_EMAIL:
            from_email = settings.DEFAULT_FROM_EMAIL

        message = EmailMultiAlternatives(
            subject, body, from_email, [self.email], **kwargs)

        if html is not None:
            message.attach_alternative(html, 'text/html')

        return message.send() > 0


class UserLogged(models.Model):
    """
    Mapping model to table user_logged.
    """
    user = models.OneToOneField(
        User,
        null=False,
        related_name="logged",
        primary_key=True
    )
    last_login = models.DateField(
        auto_now_add=True,
        blank=True
    )
    number_login_attempt = models.IntegerField(
        null=True
    )
    permissions_to_login = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = 'user_logged'


class UserSettings(models.Model):
    """
    Mapping user_settings table in Tandlr.
    """
    user = models.OneToOneField(
        User,
        null=False,
        related_name='settings'
    )
    session_confirm = models.BooleanField(
        default=True
    )
    message = models.BooleanField(
        default=True
    )
    session_cancellation = models.BooleanField(
        default=True
    )
    location_change = models.BooleanField(
        default=True
    )
    session_reminder = models.BooleanField(
        default=True
    )
    available = models.BooleanField(
        default=False
    )
    push_notifications_enabled = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = 'user_settings'


class LocationUser(models.Model):
    """
    Mapping location_user in Table.
    """
    user = models.OneToOneField(
        User,
        null=False,
        related_name='location_user'
    )

    point = models.PointField(srid=4326)

    last_modification_date = models.DateTimeField(
        auto_now_add=True
    )

    place_description = models.TextField(
        max_length=250,
        blank=True
    )
    objects = models.GeoManager()

    class Meta:
        db_table = 'location_user'


class DeviceUser(TimeStampedMixin):
    """
    Mapping device_user table in Tandlr.
    """
    user = models.ForeignKey(
        User,
        related_name='devices'
    )
    device_user_token = models.TextField(
        max_length=250,
        blank=True,
        null=True
    )

    device_os = models.CharField(
        max_length=20
    )
    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = 'device_user'
        unique_together = ("device_user_token", "user")

    def __unicode__(self):
        return '{}-{}'.format(
            self.user.username.encode('utf-8'),
            self.device_os
        ).decode('utf-8')


class UserSummary(models.Model):
    """
    Model used to save and show the sumary information of a teacher.
    """
    user = models.OneToOneField(
        User,
        null=False,
        related_name='user_summary'
    )

    score_average_teacher = models.FloatField(
        default=5.0,
        null=True,
        verbose_name=u'teacher rate'
    )

    score_average_student = models.FloatField(
        default=5.0,
        null=True,
        verbose_name=u'student rate'
    )

    sessions_as_teacher = models.PositiveIntegerField(
        default=1,
        verbose_name=_('sessions as teacher'),
        help_text=_('Defines how much sessions the user has taken as teacher')
    )

    lessons_as_student = models.PositiveIntegerField(
        default=1,
        verbose_name=_('lessons as student'),
        help_text=_('Defines how much lessons the user has taken as student')
    )

    class Meta:
        verbose_name_plural = "users summaries"
        verbose_name = "user summary"

    def __unicode__(self):
        return self.user.get_full_name()


class Teacher(User):
    """
    Proxy model used to show users, filtered by teachers inside of the admin.
    """
    class Meta:
        proxy = True
        verbose_name_plural = "teachers"
        verbose_name = "teacher"

    def __init__(self, *args, **kwargs):
        self._meta.get_field('is_teacher').default = True
        super(Teacher, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return self.get_full_name()


class Student(User):
    """
    Proxy model used to show users, filtered by students inside of the admin.
    """
    class Meta:
        proxy = True
        verbose_name_plural = "students"
        verbose_name = "student"

    def __unicode__(self):
        return self.get_full_name()
