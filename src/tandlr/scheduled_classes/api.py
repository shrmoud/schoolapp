# -*- coding: utf-8 -*-
"""
viewsets to manage session in tandlr.
"""
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone

from rest_framework import status
from rest_framework.response import Response

import stripe


from tandlr.api.v2.routers import router
from tandlr.balances.models import Balance
from tandlr.chat.models import Chat
from tandlr.core.api import mixins, viewsets
from tandlr.core.api.viewsets.nested import NestedViewset
from tandlr.notifications.models import Notification
from tandlr.scheduled_classes import serializers
from tandlr.scheduled_classes.models import (
    Class,
    ClassBill,
    RequestClassExtensionTime,
    Slot,
    Subject
)

from tandlr.scheduled_classes.permissions import (
    LessonPermission,
    SessionPermission
)

from tandlr.scheduled_classes.utils import calculate_price_per_extrension_class
from tandlr.stripe.models import StripeCard
from tandlr.stripe.serializers import StripeChargeSerializer
from tandlr.stripe.utils import (
    generate_charge_description,
    make_stripe_charge
)


class SlotViewSet(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.PartialUpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):
    permission_classes = ()

    serializer_class = serializers.SlotV2Serializer
    create_serializer_class = serializers.SlotV2Serializer
    update_serializer_class = serializers.SlotV2Serializer
    destroy_serializer_class = serializers.SlotV2Serializer
    list_serializer_class = serializers.SlotListV2Serializer
    retrieve_serializer_class = serializers.SlotListV2Serializer

    def create(self, request, *args, **kwargs):
        """
        Allows the session's user to add slots, to define his available time.
        ---
        request_serializer: serializers.SlotV2Serializer
        response_serializer: serializers.SlotListV2Serializer

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
        return super(SlotViewSet, self).create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Allows the session's user to update his profile information.
        ---
        request_serializer: serializers.SlotV2Serializer
        response_serializer: serializers.SlotListV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(SlotViewSet, self).partial_update(
            request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Allows the session's user to delete certain slot.
        ---
        request_serializer: serializers.SlotV2Serializer
        response_serializer: serializers.SlotListV2Serializer

        responseMessages:
            - code: 203
              message: NO CONTENT
            - code: 404
              message: NOT FOUND
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(SlotViewSet, self).destroy(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Allows the session's user get the information of all his slots.
        ---
        request_serializer: serializers.SlotV2Serializer
        response_serializer: serializers.SlotListV2Serializer

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
        return super(SlotViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Allows the session's user get the information for certain slot.
        ---
        request_serializer: serializers.SlotV2Serializer
        response_serializer: serializers.SlotListV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(SlotViewSet, self).retrieve(request, *args, **kwargs)

    def get_queryset(self):
        return Slot.objects.filter(
            teacher=self.request.user
        )


class LessonViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.PartialUpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    serializer_class = serializers.LessonV2Serializer
    create_serializer_class = serializers.LessonV2Serializer
    update_serializer_class = serializers.LessonV2Serializer
    list_serializer_class = serializers.LessonListV2Serializer
    retrieve_serializer_class = serializers.LessonListV2Serializer

    permission_classes = (LessonPermission,)

    def create(self, request, *args, **kwargs):
        """
        Allows the session's student create a new session. Only the students
        can create a session.
        ---
        request_serializer: serializers.LessonV2Serializer
        response_serializer: serializers.LessonListV2Serializer

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
        stripe.api_key = settings.STRIPE_PRIVATE_KEY

        #
        # Don't allow the user create a lesson if the user doesn't have an
        # associated card

        local_cards = StripeCard.objects.filter(
            customer__user=request.user
        )

        associated_card = None
        for card in local_cards:
            try:
                if card.card_id and card.customer.customer_id:
                    customer = stripe.Customer.retrieve(
                        card.customer.customer_id
                    )
                    associated_card = customer.sources.retrieve(card.card_id)
                    if associated_card:
                        #
                        # If one card is found, leave the loop
                        #
                        break
            except stripe.InvalidRequestError:
                #
                # A user can have multiple cards associated. If one of them
                # doesn't work try another
                #
                continue

        if not associated_card:
            #
            # If not valid associated card was found return an error
            #
            return Response(
                {
                    "detail": "The student doesn't have a valid card"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        #
        # When a student create a new lesson the status should be 3 (acepted)
        # or 2 (scheduled), else, the status is changed to 2 (scheduled).
        # This is because, all lessons that are requested at least 24 hours
        # after the current time, are accepted automatically, but this is
        # calculated in the frontend side.
        #
        class_status = int(request.data['class_status'])
        if class_status != 2 and class_status != 3:
            request.data['class_status'] = 2

        return super(LessonViewSet, self).create(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Allows to session's student to update the information of their
        lessons.
        ---
        request_serializer: serializers.LessonV2Serializer
        response_serializer: serializers.LessonListV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        #
        # If the lesson starts in more than 24 hours make the a complete refund
        # of the charge made previously
        #
        stripe.api_key = settings.STRIPE_PRIVATE_KEY

        session = get_object_or_404(Class, pk=kwargs['pk'])

        serializer = self.get_serializer(
            instance=session,
            data=request.data,
            partial=True,
            action='update'
        )

        if serializer.is_valid():
            if 'class_status' in serializer.validated_data:
                class_status = serializer.validated_data['class_status'].id
                now = timezone.localtime(timezone.now())

                if class_status == 7 and session.class_status_id == 3:
                    #
                    # There are two rules for refunding. If the time between
                    # the user cancelling the class and the start of the class
                    # is greater than 24 hours, then refund all the money,
                    # otherwise don't refund anything
                    #

                    #
                    # Eliminate the promotion code so the user can use it in
                    # other class
                    #
                    session.promo_code = None
                    session.save()

                    for bill in session.bills.all():
                        bill.promo_code = None
                        bill.save()

                    if (
                        (not session.meeting_now) and
                        session.class_start_date - now > timedelta(days=1)
                    ):
                        for bill in session.bills.all():
                            if bill.charge_id:
                                stripe.Refund.create(
                                    charge=bill.charge_id
                                )
                    #
                    # In the second rule if the class is of type meeting_now
                    # and the user is cancelling the class before it starts,
                    # only charge 5 dollars and refund the rest.
                    #
                    elif (
                        session.meeting_now and
                        now < session.class_start_date
                    ):
                        for bill in session.bills.all():
                            #
                            # When a session is created with a 100% promo code,
                            # bills are created without a charge_id, so there's
                            # no need to refund that bill (charge).
                            #
                            if bill.charge_id:
                                stripe.Refund.create(
                                    charge=bill.charge_id,
                                    amount=int((bill.subtotal * 100) - 500)
                                )
            else:
                return Response(
                    {
                        'detail': 'class_status is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        fixed_date_time = (
            session.class_start_date + timedelta(hours=session.time_zone_conf)
        )

        context = {
            'booking': session,
            'request': request,
            'fixed_date_time': fixed_date_time
        }

        subject_template = (
            'email/booking/'
            'booking_cancel_student_subject.txt'
        )

        body_template = (
            'email/booking/booking_cancel_student.txt'
        )

        html_template = (
            'email/booking/booking_cancel_student.html'
        )

        subject = render_to_string(
            subject_template,
            context
        ).strip()

        body = render_to_string(body_template, context)
        html = render_to_string(html_template, context)

        sender = session.student
        receiver = session.teacher
        action = 'payment cancelation'

        Notification.objects.create(
            receiver=receiver,
            sender=sender,
            target_action=action,
            target=session,
            body=subject
        )

        receiver.email_user(subject, body, html=html)

        return super(LessonViewSet, self).partial_update(
            request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Allows to session's student get the information of their lessons.
        ---
        request_serializer: serializers.LessonV2Serializer
        response_serializer: serializers.LessonListV2Serializer

        parameters:
            - name: month
              type: integer
              required: false
              in: query
            - name: year
              type: integer
              required: false
              in: query
            - name: status
              type: integer
              required: false
              in: query
              description: filter the list by status id. You can filter by
                multiples ids. For example ?status=1,2,3

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
        try:

            session_status = self.request.query_params.get('status', None)

            if session_status:
                session_status = map(int, session_status.split(','))

        except ValueError:
            return Response(
                {
                    "detail": "The lesson status should be a integer."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super(LessonViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Allows the session's student get the full information of their lesson.
        ---
        request_serializer: serializers.LessonListV2Serializer
        response_serializer: serializers.LessonListV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(LessonViewSet, self).retrieve(request, *args, **kwargs)

    def get_queryset(self):
        #
        # Get the current date.
        #
        today_date = timezone.now()

        #
        # If the status is given in the params, then, the queryset returns
        # only the sessions that has the given status of the current user,
        # else, return all sessions of the current user.
        #
        status = self.request.query_params.get('status', None)

        #
        # If the month isn't given in the params, then, the queryset returns
        # all sessions of the current user.
        #
        month = self.request.query_params.get('month', None)

        #
        # The year is an optional param, if isn't given, then we get the
        # current year and after we filter the queryset by the month and year.
        #
        year = self.request.query_params.get('year', today_date.year)

        #
        # Sessions should be ordered by class_status as follows:
        #
        #   id | name       | order
        #   -------------------------
        #    4 | On course  | 1
        #    6 | Pending    | 2
        #    3 | Acepted    | 3
        #    2 | Scheduled  | 4
        #    1 | Rejected   | 6
        #    7 | Canceled   | 7
        #

        lessons = Class.objects.filter(
            student=self.request.user,
            class_status_id__in=[1, 2, 3, 4, 6, 7]
        )

        if month:
            lessons = lessons.filter(
                class_start_date__month=month,
                class_start_date__year=year
            )

        if status:
            status_ids = map(int, status.split(','))
            lessons = lessons.filter(
                class_status__in=status_ids
            )

        return lessons.order_by('class_status__order')


class SessionViewSet(
        mixins.RetrieveModelMixin,
        mixins.PartialUpdateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """
    Session imparted by a user that acts as teacher.
    """

    serializer_class = serializers.SessionV2Serializer
    update_serializer_class = serializers.SessionV2Serializer
    list_serializer_class = serializers.SessionListV2Serializer
    retrieve_serializer_class = serializers.SessionListV2Serializer

    permission_classes = (SessionPermission, )

    def partial_update(self, request, *args, **kwargs):
        """
        Allows the session's teacher change the session status. The teacher
        only can accept or reject a session.
        ---
        request_serializer: serializers.SessionV2Serializer
        response_serializer: serializers.SessionListV2Serializer

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
        session = get_object_or_404(Class, pk=kwargs['pk'])
        serializer = self.get_serializer(
            instance=session,
            data=request.data,
            partial=True,
            action='update'
        )

        if serializer.is_valid():
            if 'class_status' in serializer.validated_data:
                class_status = serializer.validated_data['class_status'].id
                #
                # if the class_status == 3, means that the teacher has accepted
                # the request to impart a session
                #
                if class_status == 3 and session.class_status_id == 2:
                    #
                    # if the student doesn't has a customer_id means that, it
                    # hasn't registered in stripe
                    #
                    if not session.student.customer_id:
                        return Response(
                            {
                                "detail": "customer_id not registered."
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    #
                    # if the price per hour of the subject is equals to 0 we
                    # can't do the payment.
                    #
                    if session.subject.price_per_hour == 0:
                        return Response(
                            {
                                "detail": "The price to this subject "
                                          "has not yet been assigned"
                            }
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
                    elif (
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
                        # Trying to make the charge to the student.
                        #
                        stripe_charge_response = make_stripe_charge(
                            session.id,  # class_id
                            int(total * 100),  # total
                            'usd',  # currency
                            charge_description,  # description
                            session.student.customer_id,  # customer
                            None  # card_token
                        )

                    Chat.objects.get_or_create(
                        teacher=session.teacher,
                        student=session.student,
                        session=session
                    )

                    #
                    # If the creation of the charge was successful.
                    #
                    if (
                        stripe_charge_response and
                        stripe_charge_response['success']
                    ):

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

                        created_charge = StripeChargeSerializer(
                            stripe_charge_response['response']
                        )

                        #
                        # If a charge was created, then will be returned.
                        #
                        serializer.save()

                        return Response(
                            created_charge.data,
                            status=status.HTTP_200_OK
                        )
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

                        created_class = serializers.ClassDetailV2Serializer(
                            session
                        )

                        #
                        # If a charge was created, then will be returned.
                        #
                        serializer.save()

                        return Response(
                            created_class.data,
                            status=status.HTTP_201_CREATED
                        )

                    else:
                        #
                        # Changing the state of class to cancelled.
                        #
                        session.class_status_id = 7
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

                        return Response(
                            stripe_charge_response['response'],
                            status=(
                                status.HTTP_400_BAD_REQUEST
                            )
                        )
                elif class_status == 1:
                    #
                    # When the teacher reject the session
                    #

                    #
                    # Eliminate the promotion code so the user can use it
                    # again
                    #
                    session.promo_code = None
                    for bill in session.bills.all():
                        bill.promo_code = None
                        bill.save()

                    session.save()

                    return super(
                        SessionViewSet, self
                    ).partial_update(request, *args, **kwargs)

                elif class_status == 4:
                    # If the tutor started the class

                    context = {
                        'booking': session,
                        'request': request
                    }

                    subject_template = (
                        'email/booking/'
                        'booking_started_subject.txt'
                    )

                    subject = render_to_string(
                        subject_template,
                        context
                    ).strip()

                    receiver = session.student
                    sender = session.teacher
                    action = 'booking started'

                    Notification.objects.create(
                        receiver=receiver,
                        sender=sender,
                        target_action=action,
                        target=session,
                        body=subject
                    )

                    return super(
                        SessionViewSet, self
                    ).partial_update(request, *args, **kwargs)

                elif class_status == 5:
                    # The teacher should be the tutor of the class.
                    if(request.user.is_teacher and
                       session.teacher == request.user):
                        # Updating to finished, all the extensions that are
                        # linked with the class.
                        RequestClassExtensionTime.objects.filter(
                            class_request=session
                        ).update(finished=True)

                        # Updating the class to "Ended".
                        return super(
                            SessionViewSet, self
                        ).partial_update(request, *args, **kwargs)

                    else:
                        return Response(
                            {
                                'teacher': (
                                    "this user can't change the state "
                                    "of the class to 'Ended'"
                                )
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                elif class_status == 3 and session.class_status_id == 3:
                    return Response(
                        {
                            'detail': (
                                'the session has been accepted previously'
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                else:
                    return Response(
                        {
                            'detail': (
                                'the teacher only can accept, end or reject '
                                'the session'
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    {
                        'detail': 'class_status is required'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            #
            # when the serializer is not valid
            #
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

    def list(self, request, *args, **kwargs):
        """
        Allows to session's teacher get the information of their sessions.
        ---
        response_serializer: serializers.SessionListV2Serializer

        parameters:
            - name: month
              type: integer
              required: false
              in: query
            - name: year
              type: integer
              required: false
              in: query
            - name: status
              type: integer
              required: false
              in: query
              description: filter the list by status id. You can filter by
                multiples ids. For example ?status=1,2,3

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

        try:

            session_status = self.request.query_params.get('status', None)

            if session_status:
                session_status = map(int, session_status.split(','))

        except ValueError:
            return Response(
                {
                    "detail": "The session status should be a integer."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super(SessionViewSet, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Allows the session's teacher get the full information of their session.
        ---
        response_serializer: serializers.SessionListV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(SessionViewSet, self).retrieve(request, *args, **kwargs)

    def get_queryset(self):
        #
        # Get the current date.
        #
        today_date = timezone.now()

        #
        # If the status is given in the params, then, the queryset returns
        # only the sessions that has the given status of the current user,
        # else, return all sessions of the current user.
        #
        status = self.request.query_params.get('status', None)

        #
        # If the month isn't given in the params, then, the queryset returns
        # all sessions of the current user.
        #
        month = self.request.query_params.get('month', None)

        #
        # The year is an optional param, if isn't given, then we get the
        # current year and after we filter the queryset by the month and year.
        #
        year = self.request.query_params.get('year', today_date.year)

        #
        # Sessions should be ordered by class_status as follows:
        #
        #   id | name       | order
        #   -------------------------
        #    4 | On course  | 1
        #    6 | Pending    | 2
        #    3 | Acepted    | 3
        #    2 | Scheduled  | 4
        #    1 | Rejected   | 6
        #    7 | Canceled   | 7
        #

        sessions = Class.objects.filter(
            teacher=self.request.user,
            class_status_id__in=[1, 2, 3, 4, 6, 7]
        )

        if month:
            sessions = sessions.filter(
                class_start_date__month=month,
                class_start_date__year=year
            )

        if status:
            status_ids = map(int, status.split(','))
            sessions = sessions.filter(
                class_status__in=status_ids
            )

        return sessions.order_by('class_status__order')


class LessonExtensionViewSet(
        mixins.RetrieveModelMixin,
        mixins.PartialUpdateModelMixin,
        mixins.ListModelMixin,
        NestedViewset):

    parent_model = Class
    parent_model_name = 'Class'
    parent_lookup_field = 'pk'

    serializer_class = serializers.LessonExtensionBaseV2Serializer
    update_serializer_class = serializers.LessonExtensionBaseV2Serializer
    list_serializer_class = serializers.LessonExtensionV2Serializer
    retrieve_serializer_class = serializers.LessonExtensionV2Serializer

    permission_classes = (LessonPermission,)

    def partial_update(self, request, pk=None, *args, **kwargs):
        """
        Allows the session's student update the session extensions. The student
        only can accept or reject a session.
        ---
        request_serializer: serializers.LessonExtensionBaseV2Serializer
        response_serializer: serializers.LessonExtensionV2Serializer

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
        # Get user to update.
        class_extension = get_object_or_404(RequestClassExtensionTime, pk=pk)

        # Save modifications in user.
        serializer = serializers.SessionExtensionV2Serializer(
            class_extension,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            # Starting to evaluate if making a stripe charge is needed.
            if 'accepted' in serializer.validated_data:
                accepted = serializer.validated_data['accepted']

                session = class_extension.class_request

                # If extension time was accepted by a student.
                if accepted:

                    # And the student has a customer account.
                    if not session.student.customer_id:
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
                    if not session.teacher.price_per_hour != 0:
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
                    subtotal = calculate_price_per_extrension_class(
                        session.subject.price_per_hour,
                        session.class_time
                    )

                    bill = ClassBill.objects.create(
                        hourly_price=session.subject.price_per_hour,
                        number_of_hours=session.class_time,
                        subtotal=subtotal,
                        session=session
                    )

                    balance, _ = Balance.objects.get_or_create(
                        teacher=session.teacher
                    )

                    balance.bills.add(bill)
                    balance.save()

                    # Description used in the stripe charge.
                    charge_description = generate_charge_description(
                        session,
                        subtotal
                    )

                    # Trying to make the charge to the student.
                    stripe_charge_response = make_stripe_charge(
                        session.id,  # class_id
                        int(subtotal * 100),  # total
                        'usd',  # currency
                        charge_description,  # description
                        session.student.customer_id,  # customer
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

                        context = {'request': request}
                        body_template = (
                            'email/extensions/extension_accepted.txt'
                        )
                        html_template = (
                            'email/extensions/extension_accepted.html'
                        )
                        subject_template = (
                            'email/extensions/extension_accepted_subject.txt'
                        )

                        subject = render_to_string(
                            subject_template,
                            context
                        ).strip()
                        body = render_to_string(body_template, context)
                        html = render_to_string(html_template, context)

                        Notification.objects.create(
                            receiver=session.teacher,
                            sender=session.student,
                            target_action='accepted',
                            target=class_extension,
                            body=subject
                        )

                        session.teacher.email_user(subject, body, html=html)

                        return Response(
                            created_charge.data,
                            status=status.HTTP_200_OK
                        )
                    else:
                        # Changing the state of extension to finished.
                        class_extension.finished = True
                        class_extension.save()
                        context = {
                            'booking': session,
                            'request': request
                        }

                        subject_template = (
                            'email/extensions/'
                            'extension_payment_error_subject.txt'
                        )

                        subject = render_to_string(
                            subject_template,
                            context
                        ).strip()

                        #
                        # Templates to send teacher's notification & email.
                        #
                        body_template_teacher = (
                            'email/extensions/'
                            'extension_payment_error_teacher.txt'
                        )

                        html_template_teacher = (
                            'email/extensions/'
                            'extension_payment_error_teacher.html'
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
                        # Templates to send teacher's notification & email.
                        #
                        body_template_student = (
                            'email/extensions/'
                            'extension_payment_error_student.txt'
                        )

                        html_template_student = (
                            'email/extensions/'
                            'extension_payment_error_student.html'
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
                        # Defining notification receivers.
                        #
                        teacher = session.teacher
                        student = session.student
                        action = 'payment error'

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
                            target=class_extension,
                            body=subject
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
                            target=class_extension,
                            body=subject
                        )

                        return Response(
                            stripe_charge_response['response'],
                            status=(
                                status.HTTP_400_BAD_REQUEST
                            )
                        )
                else:
                    context = {'request': request}
                    body_template = 'email/extensions/extension_rejected.txt'
                    html_template = 'email/extensions/extension_rejected.html'
                    subject_template = (
                        'email/extensions/extension_rejected_subject.txt'
                    )

                    subject = render_to_string(
                        subject_template, context
                    ).strip()
                    body = render_to_string(body_template, context)
                    html = render_to_string(html_template, context)

                    Notification.objects.create(
                        receiver=session.teacher,
                        sender=session.student,
                        target_action='rejected',
                        target=class_extension,
                        body=subject
                    )

                    session.teacher.email_user(subject, body, html=html)
            # End to evaluate if making a stripe charge is needed.

            # If it's a valid request, save.
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def list(self, request, *args, **kwargs):
        """
        Return whole sessions extensions of the session's student.
        ---
        response_serializer: serializers.LessonExtensionV2Serializer

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
        return super(LessonExtensionViewSet, self).list(
            request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Return the full information of session extension of the current
        student.
        ---
        response_serializer: serializers.LessonExtensionV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(LessonExtensionViewSet, self).retrieve(request)

    def get_queryset(self):
        return RequestClassExtensionTime.objects.filter(
            class_request=self.kwargs['session_pk'],
            class_request__student=self.request.user
        )

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs['pk']
        )


class SessionExtensionViewSet(
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        NestedViewset):

    serializer_class = serializers.SessionExtensionBaseV2Serializer
    create_serializer_class = serializers.SessionExtensionBaseV2Serializer
    retrieve_serializer_class = serializers.SessionExtensionV2Serializer
    list_serializer_class = serializers.SessionExtensionV2Serializer

    permission_classes = (SessionPermission,)

    parent_model = Class
    parent_model_name = 'Class'
    parent_lookup_field = 'pk'

    def create(self, request, *args, **kwargs):
        """
        Allows the session's teacher to add session extensions.
        ---
        request_serializer: serializers.SessionExtensionDocV2Serializer
        response_serializer: serializers.SessionExtensionV2Serializer

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
        request.data['class_request'] = kwargs['session_pk']
        return super(SessionExtensionViewSet, self).create(
            request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """
        Allows the session's teacher get the whole his sessions.
        ---
        response_serializer: serializers.SessionExtensionV2Serializer
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
        return super(SessionExtensionViewSet, self).list(request)

    def retrieve(self, request, *args, **kwargs):
        """
        Allows the session's teacher get the full information of a session.
        ---
        response_serializer: serializers.SessionExtensionV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(SessionExtensionViewSet, self).retrieve(request)

    def get_object(self):
        return get_object_or_404(
            self.get_queryset(),
            pk=self.kwargs['pk']
        )

    def get_queryset(self):
        return RequestClassExtensionTime.objects.filter(
            class_request=self.kwargs['session_pk'],
            class_request__teacher=self.request.user
        )


class SubjectViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = serializers.SubjectSerializer
    retrieve_serializer_class = serializers.SubjectSerializer
    list_serializer_class = serializers.SubjectSerializer

    def list(self, request, *args, **kwargs):
        """
        Allows the retrieve of the current subjects
        ---
        response_serializer: serializers.SubjectSerializer
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
        return super(SubjectViewSet, self).list(request)

    def retrieve(self, request, *args, **kwargs):
        """
        Allows to retrieve the detailed information for a subject
        ---
        response_serializer: serializers.SubjectSerializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(SubjectViewSet, self).retrieve(request)

    def get_queryset(self):
        if not self.request.user.university:
            return Subject.objects.all().order_by('name')

        return Subject.objects.filter(
            university=self.request.user.university
        ).order_by('name')

router.register(
    r'subjects',
    SubjectViewSet,
    base_name='subjects'
)

router.register(
    r'slots',
    SlotViewSet,
    base_name="slots"
)

router.register(
    r'lessons',
    LessonViewSet,
    base_name='lessons'
)

router.register(
    r'sessions',
    SessionViewSet,
    base_name='sessions'
)

router.register_nested(
    r'lessons',
    r'extensions',
    LessonExtensionViewSet,
    parent_lookup_name='session',
    base_name='extensions'
)

router.register_nested(
    r'sessions',
    r'extensions',
    SessionExtensionViewSet,
    parent_lookup_name='session',
    base_name='extensions'
)
