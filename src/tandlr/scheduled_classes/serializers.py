# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from decimal import Decimal

from django.contrib.gis.geos import GEOSGeometry
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

from rest_framework import serializers

from tandlr.balances.models import Balance
from tandlr.chat.models import Chat
from tandlr.core.api.serializers import ModelSerializer
from tandlr.notifications.models import Notification
from tandlr.promotions.models import PromotionCode
from tandlr.promotions.serializers import PromotionCodeV2Serializer
from tandlr.reports.models import SessionSummary

from tandlr.scheduled_classes.utils import calculate_price_per_extrension_class
from tandlr.stripe.utils import (
    generate_charge_description,
    make_stripe_charge
)


from tandlr.users.models import User, UserSettings, UserSummary
from tandlr.users.serializers import (
    UserShortDetailSerializer,
    UserShortV2Serializer
)

from .models import (
    Class,
    ClassBill,
    ClassStatus,
    RequestClassExtensionTime,
    Slot,
    Subject,
    SubjectTeacher
)


class SubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = (
            'id',
            'name',
            'description',
            'price_per_hour',
            'status'
        )


class SubjectTeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = SubjectTeacher
        fields = (
            'id',
            'teacher',
            'subject',
            'status',
        )


class SubjectTeacherDetailSubjectSerializer(serializers.ModelSerializer):

    subject = SubjectSerializer()

    class Meta:
        model = SubjectTeacher
        fields = (
            'subject',
            'status'
        )


class ClassStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassStatus
        fields = (
            'id',
            'name',
            'description',
            'status',
        )


class ClassDetailSerializer(serializers.ModelSerializer):

    class_extensions = serializers.SerializerMethodField()
    subject = SubjectSerializer()

    class Meta:
        model = Class
        fields = (
            'id',
            'teacher',
            'student',
            'class_start_date',
            'class_time',
            'class_end_date',
            'class_status',
            'class_detail',
            'place_description',
            'student_feedback',
            'teacher_feedback',
            'class_extensions',
            'subject'
        )

    def get_class_extensions(self, instance):
        class_extensions = RequestClassExtensionTime.objects.filter(
            class_request=instance
        ).order_by('id')

        return RequestClassExtensionTimeSerializer(
            class_extensions,
            many=True
        ).data


class ClassSerializer(serializers.ModelSerializer):

    class_extensions = serializers.SerializerMethodField(
        required=False
    )

    class Meta:
        model = Class
        fields = (
            'id',
            'teacher',
            'student',
            'subject',
            'class_start_date',
            'class_time',
            'class_end_date',
            'class_status',
            'class_detail',
            'place_description',
            'class_extensions',
            'meeting_now'
        )

    def get_class_extensions(self, session):
        if isinstance(session, self.Meta.model):
            class_extensions = RequestClassExtensionTime.objects.filter(
                class_request=session
            ).order_by('id')

            return RequestClassExtensionTimeSerializer(
                class_extensions,
                many=True
            ).data

    def validate_teacher(self, value):

        # Valid if this user is teacher.
        if not value.is_teacher:
            raise serializers.ValidationError("No valid teacher.")

        # Validate if teacher is available .
        teacher_is_not_available = UserSettings.objects.filter(
            user_id=value.id,
            available=False
        ).exists()

        if teacher_is_not_available:
            raise serializers.ValidationError("This teacher isn't available.")

        return value

    def validate_student(self, value):

        # Valid if this user is teacher.
        if not value.is_student:
            raise serializers.ValidationError("No valid student.")

        return value

    def validate_subject(self, value):
        # Valid if subject is available .
        if not value.status:
            raise serializers.ValidationError("This subject isn't available.")

        return value

    def validate(self, data):
        """
        Custom validation.
        """

        # Validates if teacher has subject in parameters.
        if 'subject' in data and 'teacher' in data:
            is_valid_subject = SubjectTeacher.objects.filter(
                teacher=data['teacher'],
                subject=data['subject']
            ).exists()

            if not is_valid_subject:
                raise serializers.ValidationError(
                    "Teacher doesn't have this subject.")

        if 'teacher' in data and 'class_status' in data:

            # Validates if teacher is on course when status class change.
            teacher_on_course = User.objects.filter(
                pk=data['teacher'].id,
                class_teacher__class_status__name="On course",
            ).exists()

            # Get status name
            status = data['class_status'].name

            if status == "Scheduled" and teacher_on_course:

                raise serializers.ValidationError("Teacher is on Course.")

            # Get RequestClassExtensionTime.
            class_teacher = data['teacher'].class_teacher.all()
            teacher_oncourse_extension = class_teacher.filter(
                extensions_time_class__finished=False,
                extensions_time_class__accepted=True
            ).exists()

            if status == "Scheduled" and teacher_oncourse_extension:

                raise serializers.ValidationError("Teacher is on Course.")

        return data

    def create(self, validated_data):
        session = Class(**validated_data)
        session.save()

        context = {'booking': session, 'request': self.context.get('request')}
        subject_template = 'email/booking/booking_created_teacher_subject.txt'
        body_template = 'email/booking/booking_created_teacher.txt'
        html_template = 'email/booking/booking_created_teacher.html'

        subject = render_to_string(subject_template, context).strip()
        body = render_to_string(body_template, context)
        html = render_to_string(html_template, context)

        Notification.objects.create(
            receiver=session.teacher,
            sender=session.student,
            target_action=session.class_status.name.lower(),
            target=session,
            body=subject
        )

        session.teacher.email_user(subject, body, html=html)

        return session

    def update(self, instance, validated_data):
        session = super(ClassSerializer, self).update(instance, validated_data)

        if 'class_status' in validated_data:
            status = validated_data['class_status']
            action = status.name.lower()
            context = {
                'booking': session,
                'request': self.context.get('request')
            }

            # Rejected by teacher
            if status.id == 1:
                sender = session.teacher
                receiver = session.student
                subject_template = (
                    'email/booking/booking_rejected_student_subject.txt'
                )
                body_template = (
                    'email/booking/booking_rejected_student.txt'
                )
                html_template = (
                    'email/booking/booking_rejected_student.html'
                )

            # Accepted by teacher
            elif status.id == 3:
                sender = session.teacher
                receiver = session.student
                subject_template = (
                    'email/booking/booking_confirmed_student_subject.txt'
                )
                body_template = (
                    'email/booking/booking_confirmed_student.txt'
                )
                html_template = (
                    'email/booking/booking_confirmed_student.html'
                )

            # Finished
            elif status.id == 5:
                sender = session.teacher
                receiver = session.student
                subject_template = (
                    'email/booking/booking_finished_student_subject.txt'
                )
                body_template = (
                    'email/booking/booking_finished_student.txt'
                )
                html_template = (
                    'email/booking/booking_finished_student.html'
                )

                if hasattr(sender, 'user_summary'):
                    sender.user_summary.sessions_as_teacher += 1
                else:
                    sender.user_summary = UserSummary(
                        user=sender,
                        sessions_as_teacher=1
                    )

                if hasattr(receiver, 'user_summary'):
                    receiver.user_summary.lessons_as_student += 1
                else:
                    receiver.user_summary = UserSummary(
                        user=receiver,
                        lessons_as_student=1
                    )

                sender.user_summary.save()
                receiver.user_summary.save()

            else:
                return session

            subject = render_to_string(subject_template, context).strip()
            body = render_to_string(body_template, context)
            html = render_to_string(html_template, context)

            Notification.objects.create(
                receiver=receiver,
                sender=sender,
                target_action=action,
                target=session,
                body=subject
            )

            # Send email only when teacher accepted or finished a session.
            if status.id == 3 or status.id == 5:
                receiver.email_user(subject, body, html=html)

        return session


class ClassFilterSerializer(serializers.ModelSerializer):
    teacher = UserShortDetailSerializer()
    student = UserShortDetailSerializer()
    subject = SubjectSerializer()
    class_status = ClassStatusSerializer()

    class Meta:
        model = Class
        fields = (
            'id',
            'teacher',
            'student',
            'subject',
            'class_start_date',
            'class_time',
            'class_end_date',
            'class_status',
            'class_detail',
            'place_description'
        )


class RequestClassExtensionTimeSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestClassExtensionTime
        fields = (
            'id',
            'class_request',
            'time',
            'accepted',
            'finished',
            'extension_time_end_date'
        )

    def create(self, validated_data):
        session = super(RequestClassExtensionTimeSerializer, self).create(
            validated_data)

        context = {'booking': session, 'request': self.context.get('request')}
        body_template = 'email/extensions/extension_requested_student.txt'
        html_template = 'email/extensions/extension_requested_student.html'
        subject_template = (
            'email/extensions/extension_requested_student_subject.txt'
        )

        subject = render_to_string(subject_template, context).strip()
        body = render_to_string(body_template, context)
        html = render_to_string(html_template, context)

        Notification.objects.create(
            receiver=session.class_request.student,
            sender=session.class_request.teacher,
            target_action='requested',
            target=session,
            body=subject
        )

        session.class_request.student.email_user(subject, body, html=html)

        return session


class RequestClassExtensionTimeFilterSerializer(serializers.ModelSerializer):
    class_request = ClassFilterSerializer()

    class Meta:
        model = RequestClassExtensionTime
        fields = (
            'id',
            'class_request',
            'time',
            'accepted',
            'finished',
            'extension_time_end_date'
        )


class SessionStatusV2Serializer(ModelSerializer):
    class Meta:
        model = ClassStatus
        fields = (
            'id',
            'name',
            'description',
        )


class SubjectV2Serializer(ModelSerializer):
    class Meta:
        model = Subject
        fields = (
            'id',
            'name',
            'description',
            'price_per_hour',
        )


class SessionBaseV2Serializer(ModelSerializer):

    promo_code = serializers.CharField(required=False)
    longitude = serializers.FloatField(
        required=True,
        write_only=True
    )
    latitude = serializers.FloatField(
        required=True,
        write_only=True
    )

    class Meta:
        model = Class

        read_only_fields = (
            'location',
        )

        fields = (
            'id',
            'teacher',
            'student',
            'class_start_date',
            'class_time',
            'class_end_date',
            'class_status',
            'class_detail',
            'place_description',
            'student_feedback',
            'teacher_feedback',
            'subject',
            'promo_code',
            'participants',
            'location',
            'latitude',
            'longitude',
            'meeting_now'
        )

    def validate_teacher(self, value):
        # Valid if this user is teacher.
        if not value.is_teacher:
            raise serializers.ValidationError("No valid teacher.")

        return value

    def validate_student(self, value):
        # Valid if this user is teacher.
        if not value.is_student:
            raise serializers.ValidationError("No valid student.")

        return value

    def validate_promo_code(self, value):
        # Validate that the promotion code exists, is active, and has not
        # been used
        try:
            value = PromotionCode.objects.get(
                expiration_date__gt=timezone.now(),
                code__iexact=value,
                is_active=True
            )
            #
            # Analyze if the promotion code and the user have been used. The
            # reason the meta attribute "unique_together" is not used inside
            # the model Class is because it generates two problems:
            #
            # First it makes promo_code obligatory ignoring thta it could be
            # empty, this is probably a bug in the current version of Django.
            #
            # Second and more important a Null value is considered a valid
            # value, therefore the combination (user_1, null) would be invalid
            # once a student creates its first class.
            #
            classes = Class.objects.filter(
                student=self.context['request'].user,
                promo_code=value
            )
            if value.uses_per_user <= 1 and classes.count() > 0:
                raise serializers.ValidationError(
                    "This student has already used this promotion code"
                )
            elif classes.count() >= value.uses_per_user:
                raise serializers.ValidationError(
                    (
                        u"This student has already exchanged the limit of "
                        u"promotion codes"
                    )
                )

        except PromotionCode.DoesNotExist:
            raise serializers.ValidationError(
                "The promo code entered is invalid"
            )

        return value

    def validate_subject(self, value):
        # Valid if subject is available .
        if not value.status:
            raise serializers.ValidationError("This subject isn't available.")

        return value

    def validate_class_time(self, value):
        # Valid that the class time is a multiple of 30 minutes
        try:
            #
            # Transform the class into minutes
            #
            class_time_minutes = value.hour * 60 + value.minute
            if class_time_minutes % 30 != 0:
                # The class time is not a multiple of 30, return an error
                raise serializers.ValidationError(
                    "Each session should be a multiple of 30 minutes"
                )
        except ValueError:
            raise serializers.ValidationError("Incorrect class time format")

        return value

    def validate(self, data):
        """
        Validate that the teacher is available and the teacher impart the given
        subject.
        """
        if self.context['view'].action == 'create':
            #
            # Take only the sessions with status:
            #
            #   id | name       |
            #   -----------------
            #    2 | Scheduled  |
            #    3 | Acepted    |
            #    4 | On course  |
            #    6 | Pending    |
            #
            start_date = data['class_start_date']
            end_date = data['class_end_date']

            classes_at_same_time = Class.objects.filter(
                (
                    Q(class_start_date__gte=start_date) &
                    Q(class_start_date__lt=end_date)
                ) |
                (
                    Q(class_end_date__gt=start_date) &
                    Q(class_end_date__lte=end_date)
                ) |
                (
                    Q(class_start_date__lte=start_date) &
                    Q(class_end_date__gte=end_date)
                ),
                class_status_id__in=[2, 3, 4, 6],
            ).count()

            if classes_at_same_time > 0:
                raise serializers.ValidationError(
                    'The student has lessons scheduled in this time'
                )

        # If is an "on demand" session, validates if teacher is available .
        if 'meeting now' in data and data['meeting_now']:
            teacher_is_not_available = UserSettings.objects.filter(
                user_id=data['teacher'].id,
                available=False
            ).exists()

            if teacher_is_not_available:
                raise serializers.ValidationError(
                    "This teacher isn't available."
                )
        if 'class_start_date' in data and 'class_end_date' in data:
            if data['class_start_date'] > data['class_end_date']:
                raise serializers.ValidationError(
                    'The start date should be greater than end date'
                )

        if 'latitude' in data and 'longitude' in data:
            latitude = data.pop('latitude')
            longitude = data.pop('longitude')

            data['location'] = GEOSGeometry(
                'SRID=4326;POINT({0} {1})'.format(
                    latitude, longitude
                )
            )

        # Validates if teacher has subject in parameters.
        if 'subject' in data and 'teacher' in data:
            is_valid_subject = SubjectTeacher.objects.filter(
                teacher=data['teacher'],
                subject=data['subject']
            ).exists()

            if not is_valid_subject:
                raise serializers.ValidationError(
                    "Teacher doesn't have this subject.")

        if 'teacher' in data and 'class_status' in data:

            # Validates if teacher is on course when status class change.
            teacher_on_course = User.objects.filter(
                pk=data['teacher'].id,
                class_teacher__class_status__id=4,
            ).exists()

            # Get status name
            status = data['class_status'].id

            if status == 2 and teacher_on_course:

                raise serializers.ValidationError("Teacher is on Course.")

            # Get RequestClassExtensionTime.
            teacher_classes = data['teacher'].class_teacher.all()
            teacher_oncourse_extension = teacher_classes.filter(
                extensions_time_class__finished=False,
                extensions_time_class__accepted=True
            ).exists()

            if status == 2 and teacher_oncourse_extension:

                raise serializers.ValidationError("Teacher is on Course.")

        return data


class LessonV2Serializer(SessionBaseV2Serializer):

    class Meta:
        model = Class

        read_only_fields = (
            'location',
        )

        fields = (
            'id',
            'teacher',
            'student',
            'class_start_date',
            'class_time',
            'class_end_date',
            'class_status',
            'class_detail',
            'place_description',
            'student_feedback',
            'teacher_feedback',
            'subject',
            'promo_code',
            'participants',
            'location',
            'latitude',
            'longitude',
            'meeting_now',
            'time_zone_conf'
        )

    def validate_class_start_date(self, date):
        if date < timezone.now():
            raise serializers.ValidationError(
                'The start date should be greater than today'
            )
        return date

    def validate_class_end_date(self, date):
        if date < timezone.now():
            raise serializers.ValidationError(
                'The end date should be greater than today'
            )
        return date

    def validate_student(self, value):
        # Valid if this user is teacher.
        request = self.context['request']
        if not value.id == request.user.id:
            raise serializers.ValidationError(
                "The student only can create/edit a session to himself"
            )

        return value

    def update(self, instance, validated_data):
        session = super(
            LessonV2Serializer, self).update(instance, validated_data)

        if 'class_status' in validated_data:
            #
            # We validate that the status is Canceled
            #
            if validated_data['class_status'].id == 7:
                return session

        raise serializers.ValidationError(
            "The student only can cancel the session."
        )

    def create(self, validated_data):
        session = Class(**validated_data)
        fixed_date_time = (
            session.class_start_date + timedelta(hours=session.time_zone_conf)
        )
        session.save()

        #
        # If the status given is equals to 2 means that the lesson was created
        # to date wich is letter than 24 hrs.
        #
        if session.class_status.id == 2:

            context = {
                'booking': session,
                'request': self.context.get('request'),
                'fixed_date_time': fixed_date_time
            }

            subject_template = (
                'email/booking/booking_created_teacher_subject.txt'
            )
            body_template = 'email/booking/booking_created_teacher.txt'
            html_template = 'email/booking/booking_created_teacher.html'

            subject = render_to_string(subject_template, context).strip()
            body = render_to_string(body_template, context)
            html = render_to_string(html_template, context)

            Notification.objects.create(
                receiver=session.teacher,
                sender=session.student,
                target_action=session.class_status.name.lower(),
                target=session,
                body=subject
            )

            #
            # Summary model was created to reports
            #
            now = timezone.now().replace(minute=0, second=0, microsecond=0)

            session_summary, created = SessionSummary.objects.get_or_create(
                created_datetime=now
            )

            if not created:
                session_summary.count = session_summary.count + 1
                session_summary.save()

            session.teacher.email_user(subject, body, html=html)

        #
        # If the status given is equals to 3 means that the lesson was created
        # to date wich is gretter than 24 hrs. If the lesson is created with
        # status 3 it's not necessary that the teacher accept the request, it
        # is accept automaticallly.
        #
        elif session.class_status.id == 3:
            if not session.student.customer_id:
                raise serializers.ValidationError(
                    'customer_id not resgitered'
                )

            if session.subject.price_per_hour == 0:
                raise serializers.ValidationError(
                    'The price to this subject has not yet been assigned'
                )

            #
            # Price per hour of the subject
            #
            subtotal = calculate_price_per_extrension_class(
                session.subject.price_per_hour,
                session.class_time
            )

            discounts = 0
            total = subtotal

            if (
                session.promo_code is not None and
                int(session.promo_code.discount) < 100
            ):
                discounts = (
                    subtotal *
                    (session.promo_code.discount / Decimal('100.0'))
                )
                #
                # If the amount is bigger that 50 cents charge the
                # discount, otherwise charge 50 cents
                #
                if subtotal - discounts < 0.50:
                    total = 50.0 / 100.0
                else:
                    total = subtotal - discounts
            elif(
                session.promo_code is not None and
                int(session.promo_code.discount) >= 100
            ):
                #
                # If the discount of the promocode if 100 percent
                # charge only 50 cents to the user
                #
                total = 0.0

            balance, _ = Balance.objects.get_or_create(
                teacher=session.teacher
            )

            stripe_charge_response = None
            if total > 0:
                #
                # Description used in the stripe charge.
                #
                charge_description = generate_charge_description(
                    session,
                    total
                )

                #
                # Trying to make the charge to the student
                #
                stripe_charge_response = make_stripe_charge(
                    session.id,  # class_id
                    int(total * 100),  # total
                    'usd',  # currency
                    charge_description,  # description
                    session.student.customer_id,  # customer
                    None  # card_token
                )

            session.save()
            #
            # If the class was accepted already create a chat for the user
            #
            Chat.objects.get_or_create(
                teacher=session.teacher,
                student=session.student,
                session=session
            )

            #
            # If the creation of the charge was successful
            #
            if stripe_charge_response and stripe_charge_response['success']:

                bill = ClassBill.objects.create(
                    promo_code=session.promo_code,
                    hourly_price=session.subject.price_per_hour,
                    number_of_hours=session.class_time,
                    subtotal=subtotal,
                    session=session,
                    charge_id=(
                        stripe_charge_response['response'].charge_id
                    )
                )

                balance.bills.add(bill)
                balance.save()

            #
            # If the coupon used has a 100 percent discount, then
            # the charge never goes through Stripe. In that case return
            #
            #
            elif total == 0:
                bill = ClassBill.objects.create(
                    promo_code=session.promo_code,
                    hourly_price=session.subject.price_per_hour,
                    number_of_hours=session.class_time,
                    subtotal=subtotal,
                    session=session
                )

                balance.bills.add(bill)
                balance.save()

            else:
                #
                # Changing the state of class to cancelled.
                #
                session.class_status_id = 7
                request = self.context['request']
                session.save()

                fixed_date_time = (
                    session.class_start_date +
                    timedelta(hours=session.time_zone_conf)
                )

                context = {
                    'booking': session,
                    'request': request,
                    'fixed_date_time': fixed_date_time
                }

                subject_template = (
                    'email/booking/'
                    'booking_error_payment_stripe_subject.txt'
                )

                subject = render_to_string(
                    subject_template,
                    context
                ).strip()

                #
                # Defining notification receivers.
                #
                teacher = session.teacher
                student = session.student
                action = 'payment error'

                #
                # Templtes to send student's notification & email.
                #
                body_template_student = (
                    'email/booking/'
                    'booking_error_payment_stripe_student.txt'
                )

                html_template_student = (
                    'email/booking/'
                    'booking_error_payment_stripe_student.html'
                )

                body_student = render_to_string(
                    body_template_student,
                    context
                )

                html_student = render_to_string(
                    html_template_student,
                    context
                )

                #
                # Send email to student for stripe payment error
                #
                student.email_user(
                    subject,
                    body_student,
                    html=html_student
                )

                Notification.objects.create(
                    receiver=student,
                    sender=teacher,
                    target_action=action,
                    target=session,
                    body=subject
                )

                if session.meeting_now:
                    #
                    # Notifications and emails should be sent to
                    # the teacher only if the current session is
                    # "meeting now".
                    #

                    #
                    # Templtes to send teacher's notification & email.
                    #
                    body_template_teacher = (
                        'email/booking/'
                        'booking_error_payment_stripe_teacher.txt'
                    )

                    html_template_teacher = (
                        'email/booking/'
                        'booking_error_payment_stripe_teacher.html'
                    )

                    body_teacher = render_to_string(
                        body_template_teacher,
                        context
                    )
                    html_teacher = render_to_string(
                        html_template_teacher,
                        context
                    )

                    #
                    # Send email to teacher for stripe payment error
                    #
                    teacher.email_user(
                        subject,
                        body_teacher,
                        html=html_teacher
                    )

                    Notification.objects.create(
                        receiver=teacher,
                        sender=student,
                        target_action=action,
                        target=session,
                        body=subject
                    )

                raise serializers.ValidationError(
                    stripe_charge_response['response']
                )

        return session


class SessionV2Serializer(SessionBaseV2Serializer):

    def update(self, instance, validated_data):
        session = super(
            SessionV2Serializer, self).update(instance, validated_data)

        if 'class_status' in validated_data:
            status = validated_data['class_status']
            action = status.name.lower()
            fixed_date_time = (
                session.class_start_date +
                timedelta(hours=session.time_zone_conf)
            )

            context = {
                'booking': session,
                'request': self.context.get('request'),
                'fixed_date_time': fixed_date_time
            }

            sender = session.teacher
            receiver = session.student

            # Rejected by teacher
            if status.id == 1:
                subject_template = (
                    'email/booking/booking_rejected_student_subject.txt'
                )
                body_template = (
                    'email/booking/booking_rejected_student.txt'
                )
                html_template = (
                    'email/booking/booking_rejected_student.html'
                )

            # Accepted by teacher
            elif status.id == 3:
                #
                # Change time zones to UTC
                #
                fixed_date_time = (
                    session.class_start_date +
                    timedelta(hours=session.time_zone_conf)
                )
                context['fixed_date_time'] = fixed_date_time
                subject_template = (
                    'email/booking/booking_confirmed_student_subject.txt'
                )
                body_template = (
                    'email/booking/booking_confirmed_student.txt'
                )
                html_template = (
                    'email/booking/booking_confirmed_student.html'
                )

                #
                # The chat is created when the teacher accepts the session.
                #
                Chat.objects.get_or_create(
                    teacher=session.teacher,
                    student=session.student,
                    session=session
                )

            # Finished
            elif status.id == 5:
                subject_template = (
                    'email/booking/booking_finished_student_subject.txt'
                )
                body_template = (
                    'email/booking/booking_finished_student.txt'
                )
                html_template = (
                    'email/booking/booking_finished_student.html'
                )

                if hasattr(sender, 'user_summary'):
                    sender.user_summary.sessions_as_teacher += 1
                else:
                    sender.user_summary = UserSummary(
                        user=sender,
                        sessions_as_teacher=1
                    )

                if hasattr(receiver, 'user_summary'):
                    receiver.user_summary.lessons_as_student += 1
                else:
                    receiver.user_summary = UserSummary(
                        user=receiver,
                        lessons_as_student=1
                    )

                sender.user_summary.save()
                receiver.user_summary.save()

            else:
                return session

            subject = render_to_string(subject_template, context).strip()
            body = render_to_string(body_template, context)
            html = render_to_string(html_template, context)

            Notification.objects.create(
                receiver=receiver,
                sender=sender,
                target_action=action,
                target=session,
                body=subject
            )

            receiver.email_user(subject, body, html=html)

        return session


class LessonListV2Serializer(ModelSerializer):
    teacher = UserShortV2Serializer()
    student = UserShortV2Serializer()
    subject = SubjectV2Serializer()
    class_status = SessionStatusV2Serializer()
    promo_code = PromotionCodeV2Serializer()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = (
            'id',
            'teacher',
            'student',
            'class_start_date',
            'class_time',
            'class_end_date',
            'class_status',
            'class_detail',
            'place_description',
            'subject',
            'promo_code',
            'participants',
            'latitude',
            'longitude',
            'meeting_now'
        )

    def get_latitude(self, instance):
        return instance.location.x

    def get_longitude(self, instance):
        return instance.location.y


class SessionListV2Serializer(ModelSerializer):
    teacher = UserShortV2Serializer()
    student = UserShortV2Serializer()
    subject = SubjectV2Serializer()
    class_status = SessionStatusV2Serializer()
    promo_code = PromotionCodeV2Serializer()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    def get_latitude(self, instance):
        return instance.location.x

    def get_longitude(self, instance):
        return instance.location.y

    class Meta:
        model = Class
        fields = (
            'id',
            'teacher',
            'student',
            'class_start_date',
            'class_time',
            'class_end_date',
            'class_status',
            'class_detail',
            'place_description',
            'subject',
            'promo_code',
            'participants',
            'latitude',
            'longitude',
        )


class HistorySessionBillsV2Serializer(ModelSerializer):

    session = SessionListV2Serializer()
    promo_code = PromotionCodeV2Serializer()

    class Meta:
        model = ClassBill
        fields = (
            'id',
            'promo_code',
            'hourly_price',
            'number_of_hours',
            'subtotal',
            'commission',
            'commission_amount',
            'session',
            'was_paid',
            'created_at'
        )


class SessionExtensionDocV2Serializer(serializers.Serializer):
    """
    Serializer used only to show form information correctly on
    swagger documentation.
    """
    time = serializers.TimeField()


class SessionExtensionBaseV2Serializer(ModelSerializer):

    class Meta:
        model = RequestClassExtensionTime
        fields = (
            'id',
            'class_request',
            'time',
        )

    def create(self, validated_data):
        booking = super(SessionExtensionBaseV2Serializer, self).create(
            validated_data
        )

        context = {'booking': booking, 'request': self.context.get('request')}
        body_template = 'email/extensions/extension_requested_student.txt'
        html_template = 'email/extensions/extension_requested_student.html'
        subject_template = (
            'email/extensions/extension_requested_student_subject.txt'
        )

        subject = render_to_string(subject_template, context).strip()
        body = render_to_string(body_template, context)
        html = render_to_string(html_template, context)

        Notification.objects.create(
            receiver=booking.class_request.student,
            sender=booking.class_request.teacher,
            target_action='requested',
            target=booking,
            body=subject
        )

        booking.class_request.student.email_user(subject, body, html=html)

        return booking


class LessonExtensionBaseV2Serializer(ModelSerializer):
    class_request = LessonListV2Serializer()

    end_date = serializers.DateTimeField(
        source='extension_time_end_date'
    )

    class Meta:
        model = RequestClassExtensionTime
        fields = (
            'id',
            'time',
            'accepted',
            'finished',
            'end_date',
            'class_request',
        )


class LessonExtensionV2Serializer(LessonExtensionBaseV2Serializer):
    class_request = LessonListV2Serializer()

    end_date = serializers.DateTimeField(
        source='extension_time_end_date'
    )

    class Meta:
        model = RequestClassExtensionTime
        fields = (
            'id',
            'time',
            'accepted',
            'finished',
            'end_date',
            'class_request',
        )


class SessionExtensionV2Serializer(SessionExtensionBaseV2Serializer):
    class_request = SessionListV2Serializer()

    end_date = serializers.DateTimeField(
        source='extension_time_end_date'
    )

    class Meta:
        model = RequestClassExtensionTime
        fields = (
            'id',
            'time',
            'accepted',
            'finished',
            'end_date',
            'class_request',
        )


class SlotV2Serializer(ModelSerializer):

    class Meta:
        model = Slot
        fields = (
            'id',
            'teacher',
            'start_time',
            'end_time',
            'date',
            'is_unique',
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday',
        )

    def validate_teacher(self, user):
        if not user.is_teacher:
            raise serializers.ValidationError("No valid teacher.")
        if user != self.context['request'].user:
            raise serializers.ValidationError(
                "Forbidden to asign a slot to another teacher."
            )

        return user

    def validate(self, data):
        # Validating that initial time is before of final time.
        if self.instance:
            start_time = data.get('start_time', self.instance.start_time)
            end_time = data.get('end_time', self.instance.end_time)
            date = data.get('date', self.instance.date)
            is_unique = data.get('is_unique', self.instance.is_unique)
            monday = data.get('monday', self.instance.monday)
            tuesday = data.get('tuesday', self.instance.tuesday)
            wednesday = data.get('wednesday', self.instance.wednesday)
            thursday = data.get('thursday', self.instance.thursday)
            friday = data.get('friday', self.instance.friday)
            saturday = data.get('saturday', self.instance.saturday)
            sunday = data.get('sunday', self.instance.sunday)
        else:
            start_time = data.get('start_time', None)
            end_time = data.get('end_time', None)
            date = data.get('date', None)
            is_unique = data.get('is_unique', None)

            monday = data.get('monday', False)
            tuesday = data.get('tuesday', False)
            wednesday = data.get('wednesday', False)
            thursday = data.get('thursday', False)
            friday = data.get('friday', False)
            saturday = data.get('saturday', False)
            sunday = data.get('sunday', False)

        # Validating coherence of unique slots.
        if date and not is_unique:
            raise serializers.ValidationError(
                'Invalid slot, is_unique shold be True if date is given.'
            )

        # Validating consistency between start_time and end_time.
        if start_time > end_time:
            raise serializers.ValidationError(
                'Invalid time range for slot, '
                'end_time should be after start_time.'
            )

        # Validating minimun time for slot.
        minimun_expected_end_time = (
            datetime.combine(
                timezone.now().date(),
                start_time
            ) + timedelta(minutes=30)
        ).time()

        if end_time < minimun_expected_end_time:
            raise serializers.ValidationError(
                'Invalid time range for slot, '
                'minimun time for slot is 30 minutes.'
            )

        # Validating that the slot is not overlaping with another one.
        request = self.context['request']
        time_overlaped_slots = Slot.objects.filter(
            (Q(start_time__gte=start_time) & Q(start_time__lt=end_time)) |
            (Q(end_time__gt=start_time) & Q(end_time__lte=end_time)) |
            (Q(start_time__lte=start_time) & Q(end_time__gte=end_time)),
            teacher=request.user
        )

        # Excluding current instance in the overlaped query (when updating).
        if self.instance:
            time_overlaped_slots = time_overlaped_slots.exclude(
                id=self.instance.id
            )

        conditions = []
        q_conditions = Q()
        if is_unique:
            # When slot is unique, date should be provided.
            if date is None:
                raise serializers.ValidationError(
                    'Invalid date for unique slot.'
                )

            # Validation that checks if date already exists, or the
            # week day overlaps with another date.
            week_days = [
                'monday', 'tuesday', 'wednesday', 'thursday',
                'friday', 'saturday', 'sunday'
            ]
            week_day = date.weekday()

            # Appending equivalent week day of given date.
            conditions.append({week_days[week_day]: True})
            # Appending specific date.
            conditions.append({'date': date})

            for condition in conditions:
                q_conditions |= Q(**condition)

            overlaped_slots_count = time_overlaped_slots.filter(
                q_conditions
            ).count()
        else:
            # Validation that checks if the time of the given week days
            # don't overlaps with another slots.

            # Appending conditional week days that will be used to the filter.
            if monday:
                conditions.append({'monday': True})
            if tuesday:
                conditions.append({'tuesday': True})
            if wednesday:
                conditions.append({'wednesday': True})
            if thursday:
                conditions.append({'thursday': True})
            if friday:
                conditions.append({'friday': True})
            if saturday:
                conditions.append({'saturday': True})
            if sunday:
                conditions.append({'sunday': True})

            for condition in conditions:
                q_conditions |= Q(**condition)

            overlaped_slots_count = time_overlaped_slots.filter(
                q_conditions
            ).count()

        if overlaped_slots_count > 0:
            raise serializers.ValidationError(
                'Invalid time range for slot, '
                'given time range is overlaping with another one.'
            )

        return data


class SlotListV2Serializer(SlotV2Serializer):
    teacher = UserShortV2Serializer()

    class Meta:
        model = Slot
        fields = (
            'id',
            'teacher',
            'start_time',
            'end_time',
            'date',
            'is_unique',
            'monday',
            'tuesday',
            'wednesday',
            'thursday',
            'friday',
            'saturday',
            'sunday',
        )


class ClassDetailV2Serializer(serializers.ModelSerializer):

    class_extensions = serializers.SerializerMethodField()
    subject = SubjectSerializer()
    teacher = UserShortV2Serializer()
    student = UserShortV2Serializer()

    class Meta:
        model = Class
        fields = (
            'id',
            'teacher',
            'student',
            'class_start_date',
            'class_time',
            'class_end_date',
            'class_status',
            'class_detail',
            'place_description',
            'student_feedback',
            'teacher_feedback',
            'class_extensions',
            'subject'
        )

    def get_class_extensions(self, instance):
        class_extensions = RequestClassExtensionTime.objects.filter(
            class_request=instance
        ).order_by('id')

        return RequestClassExtensionTimeSerializer(
            class_extensions,
            many=True
        ).data
