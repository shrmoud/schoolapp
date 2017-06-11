# -*- coding: utf-8 -*-
import os

from django.contrib.gis.geos import Polygon
from django.shortcuts import get_object_or_404

from rest_framework import filters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from tandlr.users.models import (
    DeviceUser,
    LocationUser,
    User,
    UserLogged,
    UserSettings
)

from tandlr.users.serializers import (
    DeviceUserSerializer,
    LocationTeacherSerializer,
    LocationUserCreateSerializer,
    LocationUserSerializer,
    UserLoggedSerializer,
    UserResponseSerializer,
    UserSerializer,
    UserSettingsSerializer,
    UserShortDetailSerializer
)


class UserViewSet(viewsets.ViewSet):

    def list(self, request):
        """
        List users.
        ---

        response_serializer: UserResponseSerializer
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

        queryset = User.objects.all()

        paginator = PageNumberPagination()

        result_page = paginator.paginate_queryset(queryset, request)

        serializer_context = {'request': request}

        serializer = UserResponseSerializer(
            result_page,
            many=True,
            context=serializer_context
        )

        return paginator.get_paginated_response(serializer.data)

    def create(self, request):
        """
        Create user.
        ---

        type:
        photo:
          required: false
          type: file

        request_serializer: UserSerializer
        response_serializer: UserResponseSerializer
        omit_serializer: false

        parameters_strategy: merge
        parameters:
            - name: photo
              description: photo.
              required: false
              type: file
              paramType: file

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
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():

            # If is valid request, save.
            user = serializer.save()

            # Save encrypt password.
            user.set_password(serializer.validated_data['password'])

            user.save()

            serializer = UserResponseSerializer(
                user,
                context={'request': request}
            )

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Get specific user by primary key (id)
        ---

        response_serializer: UserResponseSerializer
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

        queryset = User.objects.all()

        user = get_object_or_404(queryset, pk=pk)

        serializer = UserResponseSerializer(
            user,
            context={'request': request}
        )

        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        """
        Partial update user.
        ---

        type:
          photo:
            required: false
            type: file

        request_serializer: UserSerializer
        response_serializer: UserResponseSerializer
        omit_serializer: false

        parameters_strategy: merge
        parameters:
            - name: photo
              description: photo.
              required: false
              type: file
              paramType: file

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
        user = get_object_or_404(User, pk=pk)

        # Save modifications in user.
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():

            # Delete image in server if user modify  photo
            if 'photo' in request.data and user.photo:
                if os.path.isfile(user.photo.path):
                    os.remove(user.photo.path)

            # If is valid request, save.
            serializer.save()

            # If password change, save encrypt password.
            if 'password' in request.data:
                user.set_password(request.data['password'])
                user.save()

            serializer = UserResponseSerializer(
                user,
                context={'request': request}
            )

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete user.
        ---

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
        user = get_object_or_404(User, pk=pk)

        if os.path.isfile(user.photo.path):
            os.remove(user.photo.path)

        # Delete user.
        user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserLoggedViewSet(viewsets.ModelViewSet):
    serializer_class = UserLoggedSerializer
    queryset = UserLogged.objects.all()


class UserSettingsViewSet(viewsets.ModelViewSet):
    serializer_class = UserSettingsSerializer
    queryset = UserSettings.objects.all()


class LocationUserViewSet(viewsets.ViewSet):

    def create(self, request):
        """
        Create or Update location user.
        ---

        request_serializer: LocationUserCreateSerializer
        response_serializer: LocationUserSerializer
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

        serializer = LocationUserCreateSerializer(data=request.data)

        if serializer.is_valid():

            user_id = self.request.user.id

            try:

                location = LocationUser.objects.get(
                    user__pk=user_id
                )

                serializer.update(location, serializer.validated_data)

                return Response(
                    LocationUserSerializer(location).data,
                    status=status.HTTP_200_OK
                )

            except LocationUser.DoesNotExist:

                location = serializer.save(user_id, serializer.validated_data)

                return Response(
                    LocationUserSerializer(location).data,
                    status=status.HTTP_201_CREATED
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete location user.
        ---

        request_serializer:  LocationUserSerializer
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

        location_user = get_object_or_404(LocationUser, pk=pk)

        location_user.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class DeviceUserViewSet(viewsets.ModelViewSet):
    serializer_class = DeviceUserSerializer
    queryset = DeviceUser.objects.all()


class UserFilterViewSet(viewsets.ReadOnlyModelViewSet):

    serializer_class = UserShortDetailSerializer
    queryset = User.objects.all()
    filter_backends = (filters.DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter,)
    search_fields = (
        'username',
        'name',
        'last_name',
        'description'
    )

    ordering_fields = (
        'id',
        'username',
        'name',
        'last_name',
        'second_last_name'
    )

    filter_fields = (
        'id',
        'username',
        'name',
        'last_name',
        'email',
        'is_active',
        'is_student',
        'is_teacher'
    )


class UserSettingsFilterViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Filter user settings.
        ---
        Optiona parameters in url:
        ---
        id (id register).
        ---
        user__id (user id).
        ---
        session_confirm (Type boolean True/False).
        ---
        message (Type boolean True/False).
        ---
        session_cancellation (Type boolean True/False).
        ---
        location_change (Type boolean True/False).
        ---
        session_reminder (Type boolean True/False).
        ---
        available (Type boolean True/False).
    ---
    """
    serializer_class = UserSettingsSerializer
    queryset = UserSettings.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)

    filter_fields = (
        'id',
        'user__id',
        'session_confirm',
        'message',
        'session_cancellation',
        'location_change',
        'session_reminder',
        'available'
    )


class TeachersByLocationViewSet(viewsets.ReadOnlyModelViewSet):
    """
        Get teachers by location and subject.
        ---
        Madatory parameters : lat_1,lat_2,lng_1,lng_2,subject,meeting_now
        ---
        lat_1,lat_2 = latitude type float, lng_1, lng_2 = longitude type float.
        ---
        subject = id subject type integer.
        ---
        meeting_now = For meeting now with teacher, type boolean (True/False)
        ---
        Example :
        ---
        lat_1=-99.189391&lat_2=-99.184767&lng_1=19.390286&lng_2=19.392391&subject=1&meeting_now=True
        ---
        Optional parameter : exclude_users_id (When you want exclude users)
        ---
        Example: exclude_users_id=1,2,3
        ---
        Example: exclude_users_id=1
        ---
    """

    serializer_class = LocationTeacherSerializer
    queryset = LocationUser.objects.all()

    def get_queryset(self):

        # Polygon parameters.
        lat_1 = self.request.query_params.get('lat_1', None)
        lat_2 = self.request.query_params.get('lat_2', None)
        lng_1 = self.request.query_params.get('lng_1', None)
        lng_2 = self.request.query_params.get('lng_2', None)

        # Parameter for exclude user.
        exclude_users_id = self.request.query_params.get(
            'exclude_users_id', None)

        # Meeting Now
        meeting_now = self.request.query_params.get('meeting_now', None)

        # Filter by subject
        subject = self.request.query_params.get('subject', None)

        # Exclude teachers
        if (lat_1 and lat_2 and lng_1 and
                lng_2 and exclude_users_id is not None):

            ne = (lat_1, lng_1,)
            sw = (lat_2, lng_2,)

            xmin = sw[0]
            ymin = ne[1]
            xmax = sw[1]
            ymax = ne[0]
            bbox = (xmin, ymin, xmax, ymax)

            geom = Polygon.from_bbox(bbox)

            # Get all teachers excluding in list exclude_users_id
            # Filter when students want take a class at moment.
            if meeting_now is not None:
                queryset = LocationUser.objects.filter(
                    user__is_teacher=True,
                    user__is_active=True,
                    user__settings__available=True
                ).exclude(
                    user__pk__in=map(int, exclude_users_id.split(','))
                )
            else:
                queryset = LocationUser.objects.filter(
                    user__is_teacher=True,
                    user__is_active=True
                ).exclude(
                    user__pk__in=map(int, exclude_users_id.split(','))
                )

            # Get all teachers in range location.
            queryset = queryset.filter(
                point__within=geom
            )

        # Not exclude teachers
        if lat_1 and lat_2 and lng_1 and lng_2 and exclude_users_id is None:

            ne = (lat_1, lng_1,)
            sw = (lat_2, lng_2,)

            xmin = sw[0]
            ymin = ne[1]
            xmax = sw[1]
            ymax = ne[0]
            bbox = (xmin, ymin, xmax, ymax)

            geom = Polygon.from_bbox(bbox)

            # Get all teachers in location
            # Filter when students want take a class at moment.
            if meeting_now is not None:
                queryset = LocationUser.objects.filter(
                    point__within=geom,
                    user__is_teacher=True,
                    user__is_active=True,
                    user__settings__available=True
                )

            else:
                queryset = LocationUser.objects.filter(
                    point__within=geom,
                    user__is_teacher=True,
                    user__is_active=True
                )

        # Filter teachers by subject
        if subject is not None and queryset:
            return queryset.filter(
                user__subject_teacher__subject__id=subject
            )

        return queryset
