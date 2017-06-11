# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone

import pytz

from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tandlr.api.v2. routers import router
from tandlr.core.api import mixins, viewsets
from tandlr.core.api.routers.single import SingleObjectRouter
from tandlr.payments.api import TeacherPaymentInformationViewSet
from tandlr.scheduled_classes.models import Class, Slot, Subject
from tandlr.users.permissions import IsSuperUser
from tandlr.users.serializers import (
    LocationTeacherV2Serializer,
    LocationsV2Serializer,
    SearchFutureTeacherV2Serializer,
    SingleLocationV2Serializer,
    UserDetailV2Serializer,
    UserSettingsRetriveV2Serializer,
    UserSettingsV2Serializer,
    UserUpdatePictureV2Serializer,
    UserV2Serializer,
)
from tandlr.utils.permissions import IsStudent, IsTeacher

from .models import DeviceUser, LocationUser


class CurrentUserViewSet(
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.PartialUpdateModelMixin,
        viewsets.GenericViewSet):

    serializer_class = UserV2Serializer
    update_serializer_class = UserV2Serializer
    retrieve_serializer_class = UserDetailV2Serializer
    change_picture_serializer_class = UserUpdatePictureV2Serializer

    def retrieve(self, request, *args, **kwargs):
        """
        Returns the information for the current session's user.
        ---
        request_serializer: UserV2Serializer
        response_serializer: UserDetailV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(CurrentUserViewSet, self).retrieve(
            request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Allows the session's user to update his profile information,
        except for the profile photo.
        ---

        request_serializer: UserV2Serializer
        response_serializer: UserDetailV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 400
              message: NOT FOUND
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(CurrentUserViewSet, self).partial_update(
            request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Allows the session's user to update his whole profile information,
        except for the profile photo.
        ---

        request_serializer: UserV2Serializer
        response_serializer: UserDetailV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 400
              message: NOT FOUND
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(CurrentUserViewSet, self).update(request, *args, **kwargs)

    @detail_route(methods=['PUT', ])
    def change_picture(self, request, *args, **kwars):
        """
        Allows the session's user to update his profile image.
        ---

        request_serializer: UserUpdatePictureV2Serializer
        response_serializer: UserDetailV2Serializer

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
        user = request.user

        # Serializer that will be used to validate the information.
        update_serializer = self.get_serializer(
            user,
            data=request.data,
            partial=True,
            action='change_picture'
        )

        update_serializer.is_valid(raise_exception=True)
        self.perform_delete_photo()
        updated_user = update_serializer.save()

        retrieve_serializer = self.get_serializer(
            updated_user,
            action='retrieve'
        )
        return Response(retrieve_serializer.data)

    @detail_route(methods=['DELETE', ])
    def delete_picture(self, request, *args, **kwars):
        """
        Allows the session's user to delete his profile image.
        ---

        responseMessages:
            - code: 204
              message: NO CONTENT
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        self.perform_delete_photo()
        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    def perform_delete_photo(self):
        user = self.request.user
        if user.photo and os.path.isfile(user.photo.path):
            os.remove(user.photo.path)
            user.photo = None
            user.save()

    def get_object(self):
        return self.request.user


class SettingsViewSet(mixins.PartialUpdateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):

    permission_classes = [IsAuthenticated]

    serializer_class = UserSettingsV2Serializer
    retrieve_serializer_class = UserSettingsRetriveV2Serializer
    update_serializer_class = UserSettingsV2Serializer

    def retrieve(self, request, pk=None):
        """
        Allows the session's user to get his settings information.
        ---

        response_serializer: UserSettingsRetriveV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(SettingsViewSet, self).retrieve(request)

    def partial_update(self, request):
        """
        Allows the session's user to update his settings information.
        ---

        request_serializer: UserSettingsV2Serializer
        response_serializer: UserSettingsRetriveV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 400
              message: BAD REQUEST
            - code: 404
              message: NOT FOUND
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        return super(SettingsViewSet, self).partial_update(request)

    def get_object(self):
        if hasattr(self.request.user, 'settings'):
            return self.request.user.settings
        else:
            return None


class LocationViewSet(mixins.UpdateModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):

    permission_classes = [IsAuthenticated, IsTeacher]

    serializer_class = SingleLocationV2Serializer
    retrieve_serializer_class = SingleLocationV2Serializer
    create_serializer_class = LocationsV2Serializer
    update_serializer_class = LocationsV2Serializer

    def retrieve(self, request, pk=None):
        """
        Get location user.
        ---

        response_serializer: SingleLocationV2Serializer
        omit_serializer: false

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
        return super(LocationViewSet, self).retrieve(request)

    def update(self, request):
        """
        Create or Update location user.
        ---

        request_serializer: LocationsV2Serializer
        response_serializer: SingleLocationV2Serializer
        omit_serializer: false

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
        return super(LocationViewSet, self).update(request)

    def get_object(self):
        if hasattr(self.request.user, 'location_user'):
            return self.request.user.location_user
        else:
            return None


class SearchTeacherViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):

    permission_classes = [IsStudent]
    serializer_class = LocationTeacherV2Serializer
    list_serializer_class = LocationTeacherV2Serializer

    def list(self, request):
        """
        Get teachers by location and subject.

        examples:

            - type: schedule_session
              search-teacher?subject=7&scheduling_datetime=2016-09-06T06:00:00.000000Z&duration=00:30&excluded_users_ids=23&timezone_conf=-5

            - type: meeting_now_session
              search-teacher?subject=5&lat_1=15.757035&lat_2=37.817035&lng_1=-80.438027&lng_2=-122.378027&exclude_users_id=21
        ---

        parameters:
            - name: subject
              description: id subject type integer.
              required: true
              type: string
              in: query

            - name: scheduling_datetime
              description: Mandatory if scheduled session.
              required: false
              type: string
              in: query

            - name: duration
              description: Mandatory if scheduled session.
              required: false
              type: string
              in: query

            - name: timezone_conf
              description: Mandatory if scheduled session.
              required: false
              type: string
              in: query

            - name: excluded_users_ids
              description: Send user ids, when you want to exclude users.
              required: false
              type: string
              in: query

            - name: lat_1
              required: false
              type: double
              in: query

            - name: lat_2
              required: false
              type: double
              in: query

            - name: lng_1
              required: false
              type: double
              in: query

            - name: lng_2
              required: false
              type: double
              in: query

        responseMessages:
            - code: 200
              message: OK
            - code: 400
              message: BAD REQUEST
            - code: 500
              message: INTERNAL SERVER ERROR

        produces:
            - application/json

        """
        now = timezone.now().replace(
            tzinfo=None,
            second=0,
            microsecond=0
        )

        now = now + timedelta(hours=1)

        #
        # If request contains scheduling_datetime.
        #
        if self.request.query_params.get('scheduling_datetime'):
            validate_scheduling = datetime.strptime(
                self.request.query_params.get('scheduling_datetime'),
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )

            if validate_scheduling < now:
                content = {'detail': 'the date should be greater than today'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        #
        # If the user doesn't have a university associated with him, return
        # and error
        #
        if self.request.user.university is None:
            content = {'detail': "user doesn't have an associated university"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super(SearchTeacherViewSet, self).list(request)

    def get_queryset(self):
        # Polygon parameters.
        lat_1 = self.request.query_params.get('lat_1')
        lat_2 = self.request.query_params.get('lat_2')
        lng_1 = self.request.query_params.get('lng_1')
        lng_2 = self.request.query_params.get('lng_2')

        scheduling_datetime = self.request.query_params.get(
            'scheduling_datetime'
        )
        duration = self.request.query_params.get('duration')

        # To calculate busy teacher, we need the certain timezone information.
        timezone_conf = self.request.query_params.get('timezone_conf')
        if timezone_conf:
            timezone_conf = int(timezone_conf)

        # Parameter for exclude user.
        excluded_users_ids = self.request.query_params.get(
            'excluded_users_ids',
            None
        )

        # Filter by subject
        subject = self.request.query_params.get('subject')

        # Base query.
        queryset = LocationUser.objects.filter(
            user__is_active=True,
            user__is_teacher=True
        )

        # Subject is mandatory.
        if subject:

            queryset = queryset.filter(
                user__subject_teacher__subject__id=subject,
                user__university=self.request.user.university
            )

            # If the scheduling_datetime was provided and all mandatory data
            # is available.
            if scheduling_datetime and duration and timezone_conf:

                start_datetime = timezone.datetime.strptime(
                    scheduling_datetime,
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                )
                #
                # Setting timezone to naive datetime value, and making the
                # query without seconds or microseconds.
                #
                utc = pytz.UTC
                start_datetime = utc.localize(start_datetime)

                # Mandatory query param to calculate the end time of the class.
                duration = timezone.datetime.strptime(
                    duration,
                    '%H:%M'
                ).time()

                busy_teachers_ids = Class.objects.filter(
                    class_start_date__year=start_datetime.year,
                    class_start_date__month=start_datetime.month,
                    class_start_date__day=start_datetime.day,
                    class_start_date__hour=start_datetime.hour,
                    class_start_date__minute=start_datetime.minute
                ).distinct(
                    'teacher__id'
                ).values_list(
                    'teacher__id',
                    flat=True
                )

                # Calculating the end datetime.
                local_start_datetime = start_datetime + timedelta(
                    hours=timezone_conf
                )

                local_end_datetime = local_start_datetime + timedelta(
                    hours=duration.hour,
                    minutes=duration.minute
                )
                start_date = local_start_datetime.date()
                start_time = local_start_datetime.time()
                end_time = local_end_datetime.time()

                week_day = local_start_datetime.weekday()

                week_days = [
                    'monday', 'tuesday', 'wednesday', 'thursday',
                    'friday', 'saturday', 'sunday'
                ]

                available_teachers_ids = Slot.objects.filter(
                    # Filter all slots with "is_unique" configuration.
                    (
                        (Q(is_unique=True) & Q(date=start_date)) |
                        # Filter all concurrent slots.
                        (Q(is_unique=False) & Q(**{week_days[week_day]: True}))
                    ) &
                    # Time should be between
                    # slot's star_time and slot's end_time
                    (
                        Q(start_time__lte=start_time) &
                        Q(end_time__gte=end_time)
                    )
                ).distinct(
                    'teacher__id'
                ).values_list(
                    'teacher__id',
                    flat=True
                )

                # If there are teachers to exclude.
                if busy_teachers_ids:
                    queryset = queryset.exclude(
                        user__pk__in=busy_teachers_ids
                    )

                # If there are teachers to include.
                queryset = queryset.filter(
                    user__pk__in=available_teachers_ids
                )

            elif lat_1 and lat_2 and lng_1 and lng_2:

                # If is meeting_now.
                bbox = (lat_2, lng_2, lat_1, lng_1)

                polygon = Polygon.from_bbox(bbox)

                # Filtering by location
                queryset = queryset.filter(
                    point__within=polygon,
                    user__settings__available=True
                )

            # If a user should be excluded.
            if excluded_users_ids:
                queryset = queryset.exclude(
                    user__pk__in=map(int, excluded_users_ids.split(','))
                )
        # Excluding session's user.
        return queryset.exclude(user__pk=self.request.user.id)


class SearchFutureTeacherViewSet(
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):

    permission_classes = [IsStudent]
    serializer_class = SearchFutureTeacherV2Serializer
    list_serializer_class = SearchFutureTeacherV2Serializer

    def list(self, request):
        """
        Returns a list of teachers in a coordinates range 7 days after of given
        date.

        examples:

            - type: schedule_session
              search-future-teacher?subject=7&scheduling_datetime=2016-09-06T06:00:00.000000Z&duration=00:30&excluded_users_ids=23&timezone_conf=-5

            - type: meeting_now_session
              search-future-teacher?subject=5&lat_1=15.757035&lat_2=37.817035&lng_1=-80.438027&lng_2=-122.378027&exclude_users_id=21
        ---
        response_serializer: LocationTeacherV2Serializer

        responseMessages:
            - code: 200
              message: OK
            - code: 400
              message: BAD REQUEST
            - code: 404
              message: NOT FOUND
            - code: 500
              message: INTERNAL SERVER ERROR

        parameters:
            - name: subject
              description: id subject type integer.
              required: true
              type: string
              in: query

            - name: scheduling_datetime
              description: Mandatory if scheduled session.
              required: false
              type: string
              in: query

            - name: duration
              description: Mandatory if scheduled session.
              required: false
              type: string
              in: query

            - name: timezone_conf
              description: Mandatory if scheduled session.
              required: false
              type: string
              in: query

            - name: excluded_users_ids
              type: Array
              in: query

        consumes:
            - application/json
        produces:
            - application/json
        """
        now = timezone.now().replace(
            tzinfo=None,
            second=0,
            microsecond=0
        )

        now = now + timedelta(hours=1)

        #
        # If request contains scheduling_datetime.
        #
        if self.request.query_params.get('scheduling_datetime'):
            validate_scheduling = datetime.strptime(
                self.request.query_params.get('scheduling_datetime'),
                "%Y-%m-%dT%H:%M:%S.%fZ"
            )

            if validate_scheduling < now:
                content = {'detail': 'the date should be greater than today'}
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        #
        # If the user doesn't have a university associated with him, return
        # and error
        #
        if self.request.user.university is None:
            content = {'detail': "user doesn't have an associated university"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        return super(SearchFutureTeacherViewSet, self).list(request)

    def get_queryset(self):

        scheduling_datetime = self.request.query_params.get(
            'scheduling_datetime'
        )
        duration = self.request.query_params.get('duration')

        # To calculate busy teacher, we need the certain timezone information.
        timezone_conf = self.request.query_params.get('timezone_conf')

        if timezone_conf:
            timezone_conf = int(timezone_conf)

        # Parameter for exclude user.
        excluded_users_ids = self.request.query_params.get(
            'excluded_users_ids',
            ''
        ).split(',')

        # Filter by subject
        subject = self.request.query_params.get('subject')

        # Subject is mandatory.
        available_dates = []
        if subject:

            # If the scheduling_datetime was provided and all mandatory data
            # is available.
            if scheduling_datetime and duration and timezone_conf:

                start_datetime = timezone.datetime.strptime(
                    scheduling_datetime,
                    '%Y-%m-%dT%H:%M:%S.%fZ'
                )
                #
                # Setting timezone to naive datetime value, and making the
                # query without seconds or microseconds.
                #
                utc = pytz.UTC
                start_datetime = utc.localize(start_datetime)

                # Mandatory query param to calculate the end time of the class.
                duration = timezone.datetime.strptime(
                    duration,
                    '%H:%M'
                ).time()

                # Calculating the end datetime.
                local_start_datetime = start_datetime + timedelta(
                    hours=timezone_conf
                )
                start_date = local_start_datetime.date()

                initial_day = local_start_datetime
                days = []
                available_slots = Slot.objects.exclude(
                    date__lt=start_date
                )
                available_teachers_ids = []
                week_days = [
                    'monday', 'tuesday', 'wednesday', 'thursday',
                    'friday', 'saturday', 'sunday'
                ]

                #
                # calculate the next 7 dates starting from given date
                #
                for i in range(0, 8):
                    days.append(initial_day + timedelta(days=i))

                for current_day in days:
                    for slot in available_slots:
                        teacher = slot.teacher
                        session_user = self.request.user

                        #
                        # - Discard if the current day dont belogs to slot
                        # - The end-point just search the frist 3 available
                        #   teachers
                        # - Each teacher just can be add 1 time in suggestion
                        # - If slots teacher is given in excluded_teachers_ids,
                        #   then, we don't add it in the results
                        # - Discard the user sessions
                        # - The teacher should be impart sessions in the same
                        #   university that current user
                        # - Return just the teachers that impart the given
                        #   subject
                        #
                        slot_is_unique_valid = (
                            slot.is_unique and
                            current_day.date() == slot.date
                        )

                        slot_is_not_unique_valid = getattr(
                            slot, week_days[current_day.weekday()]
                        )

                        user_is_valid = (
                            len(available_teachers_ids) < 3 and
                            teacher.id not in available_teachers_ids and
                            teacher.id not in excluded_users_ids and
                            teacher.id != session_user.id and
                            teacher.university == session_user.university and
                            teacher.subject_teacher.filter(
                                subject_id=subject
                            ).exists()
                        )

                        if (user_is_valid and
                                (slot_is_not_unique_valid or
                                    slot_is_unique_valid)):
                            #
                            # Define the date of the weekday of slot to
                            # filter the classes that exists in this date and
                            # after of time define in the slot.
                            #
                            initial_time = datetime(
                                current_day.year,
                                current_day.month,
                                current_day.day,
                                slot.start_time.hour,
                                slot.start_time.minute,
                                tzinfo=current_day.tzinfo
                            )

                            #
                            # Define the date of weekday of slot to after
                            # filter the classes that exists in this date and
                            # before of time define in the slot.
                            #
                            limit_time = datetime(
                                current_day.year,
                                current_day.month,
                                current_day.day,
                                slot.end_time.hour,
                                slot.end_time.minute,
                                tzinfo=current_day.tzinfo
                            )

                            #
                            # Get the classes that are in a range which is
                            # created with the date of dates starting by
                            # given date and hours/minutes of current slot.
                            #
                            classes = Class.objects.filter(
                                class_start_date__gte=initial_time,
                                class_start_date__lte=limit_time,
                                class_end_date__gte=initial_time,
                                class_end_date__lte=limit_time
                            ).distinct('teacher_id')

                            #
                            # Total hours is the sum of sessions duration that
                            # are scheduling in the date of current slot. We
                            # init the variable with the duration of the
                            # session that the user want to scheduling.
                            #
                            total_hours = timedelta(
                                    hours=duration.hour,
                                    minutes=duration.minute
                            )

                            #
                            # The hours available in the slot
                            #
                            limit_hours = (
                                timedelta(
                                    hours=slot.end_time.hour,
                                    minutes=slot.end_time.minute
                                ) - timedelta(
                                    hours=slot.start_time.hour,
                                    minutes=slot.start_time.minute
                                )
                            )

                            #
                            # Sum the duration time of the all sessions that
                            # are scheduling in the date/time of current slot.
                            #
                            for session in classes:
                                total_hours += timedelta(
                                    hours=session.class_time.hour,
                                    minutes=session.class_time.minute
                                )

                            #
                            # Total hours scheduling should be limit hours of
                            # slot.
                            #
                            if (total_hours <= limit_hours):
                                #
                                # Build the initial_time_slot with the date and
                                # the start time of slot
                                #
                                initial_time_slot = datetime(
                                    current_day.year,
                                    current_day.month,
                                    current_day.day,
                                    slot.start_time.hour,
                                    slot.start_time.minute
                                )

                                #
                                # The firts limit_time_slot is the sum beetwen
                                # the initial_time_slot and the duration of
                                # session that the user want to schedulind
                                #
                                limit_time_slot = (
                                    initial_time_slot + timedelta(
                                        hours=duration.hour,
                                        minutes=duration.minute
                                    )
                                )

                                #
                                # search the time wich can used by the user to
                                # scheduling a session
                                #
                                for session in classes:
                                    #
                                    # Search sessions wich are scheduled in
                                    # the slots of size of the given duration
                                    #
                                    session_curr_hour = Class.objects.filter(
                                        class_start_date__gte=(
                                            initial_time_slot
                                        ),
                                        class_end_date__lte=limit_time_slot
                                    ).distinct('teacher_id')

                                    #
                                    # If dont exists any session mean that the
                                    # session can be scheduling in this slot.
                                    #
                                    if (not session_curr_hour.exists() and
                                            teacher.id not in
                                            available_teachers_ids):

                                        #
                                        # Add the slot in the array that will
                                        # be returned as result.
                                        #
                                        available_dates.append({
                                            'slot': slot,
                                            'date': initial_time_slot,
                                            'teacher': slot.teacher
                                        })

                                        available_teachers_ids.append(
                                                teacher.id
                                        )

                                #
                                # If any class is included in the current slot,
                                # that means that, we can include the teacher
                                # as available
                                #
                                if not classes.exists():
                                    available_dates.append({
                                        'slot': slot,
                                        'date': initial_time_slot,
                                        'teacher': slot.teacher
                                    })

                                    available_teachers_ids.append(
                                        teacher.id
                                    )

                if len(available_dates) == 0:
                    # if the queryset is empty, then, we send a email to
                    # Tandlr admins
                    context = {
                        'subject': Subject.objects.get(pk=subject),
                        'request': self.request,
                        'scheduling_datetime': local_start_datetime,
                        'duration': duration,
                        'user': ' - '.join([
                            self.request.user.get_full_name(),
                            self.request.user.email
                        ])
                    }

                    subject_template = (
                        'email/user/search_without_results_subject.txt'
                    )
                    body_template = 'email/user/search_without_results.txt'
                    html_template = 'email/user/search_without_results.html'

                    subject = render_to_string(
                            subject_template, context
                    ).strip()
                    body = render_to_string(body_template, context)
                    html = render_to_string(html_template, context)

                    message = EmailMultiAlternatives(
                        subject,
                        body,
                        settings.DEFAULT_FROM_EMAIL,
                        settings.REPORT_EMAILS
                    )

                    if html is not None:
                        message.attach_alternative(html, 'text/html')
                        message.send()

        return available_dates


class DeviceUserViewSet(viewsets.GenericViewSet):

    permission_classes = [IsAuthenticated, IsSuperUser]
    queryset = DeviceUser.objects.all()

    @detail_route(methods=['delete'])
    def delete_all(self, request, *args, **kwargs):
        """
        Allows delete devicer exists
        ---
        responseMessages:
            - code: 203
              message: OK
            - code: 404
              message: NOT FOUND
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        self.queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

router.register(
    r'search-future-teacher',
    SearchFutureTeacherViewSet,
    base_name="search-future-teacher",
)

router.register(
    r'search-teacher',
    SearchTeacherViewSet,
    base_name="search-teacher",
)

router.register(
    r'me/location',
    LocationViewSet,
    base_name="locations",
    router_class=SingleObjectRouter,
)

router.register(
    r'me/settings',
    SettingsViewSet,
    base_name="settings",
    router_class=SingleObjectRouter,
)

router.register(
    r'me/payment-information',
    TeacherPaymentInformationViewSet,
    base_name='payment-information',
    router_class=SingleObjectRouter
)

router.register(
    r'me',
    CurrentUserViewSet,
    base_name='me',
    router_class=SingleObjectRouter
)

router.register(
    r'device',
    DeviceUserViewSet,
    base_name='device-delete',
    router_class=SingleObjectRouter
)
