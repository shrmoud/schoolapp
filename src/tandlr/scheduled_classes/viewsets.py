# -*- coding: utf-8 -*-
import datetime

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from rest_framework import (
    filters,
    status,
    viewsets
)

from rest_framework.response import Response

from tandlr.notifications.models import Notification
from tandlr.scheduled_classes.models import (
    Class,
    ClassStatus,
    RequestClassExtensionTime,
    Subject,
    SubjectTeacher
)

from tandlr.scheduled_classes.serializers import (
    ClassFilterSerializer,
    ClassSerializer,
    ClassStatusSerializer,
    RequestClassExtensionTimeFilterSerializer,
    RequestClassExtensionTimeSerializer,
    SubjectSerializer,
    SubjectTeacherSerializer
)
from tandlr.stripe.serializers import StripeChargeSerializer
from tandlr.stripe.utils import generate_charge_description, make_stripe_charge

from .utils import calculate_price_per_extrension_class


class SubjectViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectSerializer
    queryset = Subject.objects.all()


class SubjectTeacherViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectTeacherSerializer
    queryset = SubjectTeacher.objects.all()


class ClassStatusViewSet(viewsets.ModelViewSet):
    serializer_class = ClassStatusSerializer
    queryset = ClassStatus.objects.all()


class ClassViewSet(viewsets.ViewSet):

    def create(self, request):
        """
        Create schedule class.
        ---

        serializer: ClassSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
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

        # Set request data to user serializer.
        serializer = ClassSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():

            # If is valid request, save.
            serializer.create(
                validated_data=serializer.validated_data
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Get specific class by primary key (id)
        ---

        serializer: ClassSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
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

        schedule_class = get_object_or_404(Class, pk=pk)

        serializer = ClassSerializer(schedule_class)

        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        """
        Partial update class.
        ---

        serializer: ClassSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
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

        # Get class to update.
        schedule_class = get_object_or_404(Class, pk=pk)

        # Save modifications in class.
        serializer = ClassSerializer(
            schedule_class,
            data=request.data,
            partial=True,
            context={'request': request}
        )

        if serializer.is_valid():

            # Starting to evaluate if making a stripe charge is needed.
            if 'class_status' in serializer.validated_data:
                class_status = serializer.validated_data['class_status']

                # if class was accepted by a teacher
                if class_status.id == 3:

                    # And the student has a customer account.
                    if not schedule_class.student.customer_id:
                        return Response(
                            {
                                'error_message': (
                                    "Student doesn't have a stripe "
                                    "customer account."
                                )
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Amount shoudn't be 0.
                    if not schedule_class.teacher.price_per_hour(
                        schedule_class.subject.id
                    ) != 0:
                        return Response(
                            {
                                'error_message': (
                                    "Teacher price per hour shouldn't "
                                    "be 0."
                                )
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Right now, duration is not given in the serializer
                    # information, so let's assume that is just an hour.
                    time = datetime.time(1, 0, 0)

                    # Stripe API receives amount in cents.
                    amount = calculate_price_per_extrension_class(
                        schedule_class.teacher.price_per_hour(
                            schedule_class.subject.id
                        ),
                        time
                    )

                    # Description used in the stripe charge.
                    charge_description = generate_charge_description(
                        schedule_class, amount
                    )

                    # Trying to make the charge to the student.
                    stripe_charge_response = make_stripe_charge(
                        schedule_class.id,  # class_id
                        int(amount * 100),  # amount
                        'usd',  # currency
                        charge_description,  # description
                        schedule_class.student.customer_id,  # customer
                        None  # card_token
                    )

                    # If the creation of the charge was successful.
                    if stripe_charge_response['success']:
                        created_charge = StripeChargeSerializer(
                            stripe_charge_response['response']
                        )

                        # If a charge was created, then will be
                        # returned.
                        serializer.save()
                        return Response(
                            created_charge.data,
                            status=status.HTTP_200_OK
                        )
                    else:
                        # Changing the state of class to cancelled.
                        schedule_class.class_status_id = 7
                        schedule_class.save()

                        context = {
                            'booking': schedule_class,
                            'request': request
                        }

                        subject_template = (
                            'email/booking/'
                            'booking_error_payment_stripe_subject.txt'
                        )

                        body_template = (
                            'email/booking/booking_error_payment_stripe.txt'
                        )

                        html_template = (
                            'email/booking/booking_error_payment_stripe.html'
                        )

                        subject = render_to_string(
                            subject_template,
                            context
                        ).strip()
                        body = render_to_string(body_template, context)
                        html = render_to_string(html_template, context)

                        sender = schedule_class.teacher
                        receiver = schedule_class.student
                        action = 'payment error'

                        Notification.objects.create(
                            receiver=receiver,
                            sender=sender,
                            target_action=action,
                            target=schedule_class,
                            body=subject
                        )

                        receiver.email_user(subject, body, html=html)

                        return Response(
                            stripe_charge_response['response'],
                            status=(
                                status.HTTP_400_BAD_REQUEST
                            )
                        )
                # If the teacher is ending the class.
                elif class_status.id == 5:
                    # The teacher should be the tutor of the class.
                    if(request.user.is_teacher and
                       schedule_class.teacher == request.user):
                        # Updating to finished, all the extensions that are
                        # linked with the class.
                        RequestClassExtensionTime.objects.filter(
                            class_request=schedule_class
                        ).update(finished=True)
                    else:
                        return Response(
                            {
                                "teacher": (
                                    "this user can't change the state "
                                    "of the class to 'Ended'"
                                )
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

            # End to evaluate if making a stripe charge is needed.

            # If it's a valid request, save.
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete Class.
        ---

        request_serializer: ClassSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
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

        # Get user to delete.
        schedule_class = get_object_or_404(Class, pk=pk)

        # Delete user.
        schedule_class.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ClassFilterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Filter Class.
    ---
    Ordering.
    ---
    ordering : id,teacher,student,subject
    ---
    ordering : class_start_date,class_time
    ---
    ordering : class_end_date
    ---
    Example : ordering=id (ASC)
    ---
    Example : ordering=id (DESC)
    ---
    Filters.
    ---
    Fields filter : id, teacher , student,subject
    ---
    Fields filter : class_start_date,class_time,class_end_date
    ---
    Fields filter : class_status
    ---
    """

    serializer_class = ClassFilterSerializer
    queryset = Class.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,)

    ordering_fields = (
        'id',
        'teacher',
        'student',
        'subject',
        'class_start_date',
        'class_time',
        'class_end_date'
    )

    filter_fields = (
        'id',
        'teacher__id',
        'student__id',
        'subject__id',
        'class_start_date',
        'class_time',
        'class_end_date',
        'class_status__id'
    )


class RequestClassExtensionTimeViewSet(viewsets.ModelViewSet):
    serializer_class = RequestClassExtensionTimeSerializer
    queryset = RequestClassExtensionTime.objects.all()

    def partial_update(self, request, pk=None):
        """
        Partial update request class extension time.
        ---

        serializer: RequestClassExtensionTimeSerializer
        omit_serializer: false

        responseMessages:
            - code: 200
              message: OK
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

        # Get user to update.
        class_extension = get_object_or_404(RequestClassExtensionTime, pk=pk)

        # Save modifications in user.
        serializer = RequestClassExtensionTimeSerializer(
            class_extension,
            data=request.data, partial=True
        )

        if serializer.is_valid():
            # Starting to evaluate if making a stripe charge is needed.
            if 'accepted' in serializer.validated_data:
                accepted = serializer.validated_data['accepted']

                schedule_class = class_extension.class_request

                # If extension time was accepted by a student.
                if accepted:

                    # And the student has a customer account.
                    if not schedule_class.student.customer_id:
                        return Response(
                            {
                                'error_message': (
                                    "Student doesn't have a stripe "
                                    "customer account."
                                )
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Amount shoudn't be 0.
                    if not schedule_class.teacher.price_per_hour(
                        schedule_class.subject.id
                    ) != 0:
                        return Response(
                            {
                                'error_message': (
                                    "Teacher price per hour shouldn't "
                                    "be 0."
                                )
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    # Stripe API receives amount in cents.
                    amount = calculate_price_per_extrension_class(
                        schedule_class.teacher.price_per_hour(
                            schedule_class.subject.id
                        ),
                        class_extension.time
                    )

                    # Description used in the stripe charge.
                    charge_description = generate_charge_description(
                        schedule_class, amount
                    )

                    # Trying to make the charge to the student.
                    stripe_charge_response = make_stripe_charge(
                        schedule_class.id,  # class_id
                        int(amount * 100),  # amount
                        'usd',  # currency
                        charge_description,  # description
                        schedule_class.student.customer_id,  # customer
                        None  # card_token
                    )

                    # If the creation of the charge was successful.
                    if stripe_charge_response['success']:
                        created_charge = StripeChargeSerializer(
                            stripe_charge_response['response']
                        )

                        # If a charge was created, then will be
                        # returned.
                        serializer.save()
                        return Response(
                            created_charge.data,
                            status=status.HTTP_200_OK
                        )
                    else:
                        # Changing the state of extension to finished.
                        class_extension.finished = True
                        class_extension.save()
                        return Response(
                            stripe_charge_response['response'],
                            status=(
                                status.HTTP_400_BAD_REQUEST
                            )
                        )
            # End to evaluate if making a stripe charge is needed.

            # If it's a valid request, save.
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestClassExtensionTimeFilterViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Filter Request class extension time.
    ---
    Ordering.
    ---
    ordering : id, class_request, extension_time_end_date
    ---
    Example : ordering=id (ASC)
    ---
    Example : ordering=id (DESC)
    ---
    Filters.
    ---
    Fields filter : id, class_request , time
    ---
    Fields filter : accepted, finished , extension_time_end_date
    ---
    ---
    Special filter : teacher, student  (Is a number, example : teacher=1)
    ---
    """

    serializer_class = RequestClassExtensionTimeFilterSerializer
    queryset = RequestClassExtensionTime.objects.all()
    filter_backends = (filters.DjangoFilterBackend, filters.OrderingFilter,)

    ordering_fields = (
        'id',
        'class_request'
    )

    filter_fields = (
        'id',
        'class_request__id',
        'time',
        'accepted',
        'finished'
    )

    def get_queryset(self):
        queryset = RequestClassExtensionTime.objects.all()

        teacher = self.request.query_params.get('teacher', None)
        student = self.request.query_params.get('student', None)

        if teacher and student:
            return queryset.filter(
                class_request__teacher__id=teacher,
                class_request__student__id=student
            )

        if teacher:
            return queryset.filter(
                class_request__teacher__id=teacher
            )

        if student:
            return queryset.filter(
                class_request__student__id=student
            )

        return queryset
