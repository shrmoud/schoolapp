# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers

from tandlr.catalogues.serializers import UniversityV2Serializers
from tandlr.core.api.serializers import ModelSerializer

from .models import DeviceUser, LocationUser, User, UserLogged, UserSettings


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'birthday',
            'description',
            'email',
            'password',
            'gender',
            'university',
            'is_active',
            'is_student',
            'is_teacher',
            'last_name',
            'name',
            'phone',
            'photo',
            'thumbnail',
            'register_date',
            'second_last_name',
            'username',
            'zip_code',
        )


class UserResponseSerializer(serializers.ModelSerializer):
    university = UniversityV2Serializers()

    class Meta:
        model = User
        fields = (
            'id',
            'birthday',
            'description',
            'email',
            'gender',
            'university',
            'is_active',
            'is_student',
            'is_teacher',
            'last_name',
            'name',
            'phone',
            'photo',
            'thumbnail',
            'register_date',
            'second_last_name',
            'username',
            'zip_code',
        )


class UserStripeDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'name',
            'last_name',
            'second_last_name',
            'description',
            'email',
        )


class UserShortDetailSerializer(serializers.ModelSerializer):

    number_sessions_as_a_teacher = serializers.SerializerMethodField()
    number_sessions_as_a_student = serializers.SerializerMethodField()
    rating_as_a_teacher = serializers.SerializerMethodField()
    rating_as_a_student = serializers.SerializerMethodField()
    price_per_hour = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'name',
            'last_name',
            'second_last_name',
            'description',
            'photo',
            'thumbnail',
            'email',
            'phone',
            'zip_code',
            'birthday',
            'gender',
            'is_student',
            'is_teacher',
            'is_active',
            'number_sessions_as_a_teacher',
            'number_sessions_as_a_student',
            'rating_as_a_teacher',
            'rating_as_a_student',
            'price_per_hour'
        )

    def get_price_per_hour(self, obj):
        """
        Returns status price per hour, this is only used in the v1 of the API.
        """
        return settings.DEFAULT_CLASS_PRICE_PER_HOUR

    def get_number_sessions_as_a_teacher(self, obj):

        # Count sessions as a teacher.
        count_class = obj.class_teacher.filter(
            class_status__name="Ended", teacher__pk=obj.id
        ).count()

        return count_class

    def get_number_sessions_as_a_student(self, obj):

        # Count sessions as a student.
        count_class = obj.class_student.filter(
            class_status__name="Ended", student__pk=obj.id
        ).count()

        return count_class

    def get_rating_as_a_teacher(self, obj):

        try:
            return round(obj.user_summary.score_average_teacher, 2)
        except ObjectDoesNotExist:
            return 0
        except TypeError:
            return 0

    def get_rating_as_a_student(self, obj):

        try:
            return round(obj.user_summary.score_average_student, 2)
        except ObjectDoesNotExist:
            return 0
        except TypeError:
            return 0


class UserLoggedSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserLogged
        fields = (
            'user',
            'last_login',
            'number_login_attempt',
            'permissions_to_login'
        )


class UserSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserSettings
        fields = (
            'id',
            'user',
            'session_confirm',
            'message',
            'session_cancellation',
            'location_change',
            'session_reminder',
            'available',
            'push_notifications_enabled'
        )


class DeviceUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceUser
        fields = (
            'id',
            'user',
            'device_user_token',
            'device_os',
            'is_active'
        )


class LocationUserCreateSerializer(serializers.Serializer):

    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    place_description = serializers.CharField(
        max_length=250,
        allow_blank=False
    )

    def save(self, user_id, validated_data):

        # Make point
        lat = validated_data['latitude']

        lng = validated_data['longitude']

        point = GEOSGeometry('SRID=4326;POINT({0} {1})'.format(lat, lng))

        user = User.objects.get(pk=user_id)

        return LocationUser.objects.create(
            user=user,
            point=point,
            place_description=validated_data['place_description']
        )

    def update(self, instance, validated_data):

        # Make point
        lat = validated_data['latitude']

        lng = validated_data['longitude']

        point = GEOSGeometry('SRID=4326;POINT({0} {1})'.format(lat, lng))

        instance.point = point

        instance.place_description = validated_data['place_description']

        return instance.save()


class LocationUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = LocationUser
        fields = (
            'id',
            'user',
            'point',
            'last_modification_date',
            'place_description'
        )


class LocationTeacherSerializer(serializers.ModelSerializer):

    user = UserShortDetailSerializer()

    class Meta:
        model = LocationUser
        fields = (
            'user',
            'place_description'
        )


class UserDetailV2Serializer(serializers.ModelSerializer):

    sessions_as_a_teacher = serializers.SerializerMethodField()
    sessions_as_a_student = serializers.SerializerMethodField()
    rating_as_a_teacher = serializers.SerializerMethodField()
    rating_as_a_student = serializers.SerializerMethodField()
    university = UniversityV2Serializers()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'name',
            'last_name',
            'second_last_name',
            'description',
            'photo',
            'thumbnail',
            'email',
            'phone',
            'zip_code',
            'birthday',
            'gender',
            'university',
            'is_student',
            'is_teacher',
            'is_active',
            'sessions_as_a_teacher',
            'sessions_as_a_student',
            'rating_as_a_teacher',
            'rating_as_a_student',
        )

    def get_sessions_as_a_teacher(self, instance):
        return instance.sessions_as_teacher

    def get_sessions_as_a_student(self, instance):
        return instance.sessions_as_student

    def get_rating_as_a_teacher(self, instance):
        return instance.get_rating_as_a_teacher()

    def get_rating_as_a_student(self, instance):
        return instance.get_rating_as_a_student()


class UserUpdatePictureV2Serializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=True)

    class Meta:
        model = User
        fields = ('photo', )

    def validate(self, data):
        if 'photo' not in data:
            raise serializers.ValidationError("photo is a required field.")
        return data


class UserV2Serializer(ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'birthday',
            'description',
            'email',
            'password',
            'gender',
            'is_active',
            'is_student',
            'is_teacher',
            'last_name',
            'name',
            'phone',
            'register_date',
            'second_last_name',
            'username',
            'zip_code',
            'gender',
            'university',
        )


class UserShortV2Serializer(ModelSerializer):
    sessions_as_a_teacher = serializers.SerializerMethodField()
    sessions_as_a_student = serializers.SerializerMethodField()
    rating_as_a_teacher = serializers.SerializerMethodField()
    rating_as_a_student = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'name',
            'last_name',
            'second_last_name',
            'email',
            'photo',
            'thumbnail',
            'sessions_as_a_teacher',
            'sessions_as_a_student',
            'rating_as_a_teacher',
            'rating_as_a_student',
        )

    def get_sessions_as_a_teacher(self, instance):
        return instance.sessions_as_teacher

    def get_sessions_as_a_student(self, instance):
        return instance.sessions_as_student

    def get_rating_as_a_teacher(self, instance):
        return instance.get_rating_as_a_teacher()

    def get_rating_as_a_student(self, instance):
        return instance.get_rating_as_a_student()


class UserSettingsV2Serializer(serializers.ModelSerializer):

    user = serializers.SerializerMethodField()

    class Meta:
        model = UserSettings
        fields = (
            'id',
            'user',
            'session_confirm',
            'message',
            'session_cancellation',
            'location_change',
            'session_reminder',
            'available',
            'push_notifications_enabled'
        )

    def get_user(self, instance):
        user = self.context['request'].user
        return user.id


class UserSettingsRetriveV2Serializer(UserSettingsV2Serializer):
    user = UserShortV2Serializer()


# Locations


class LocationsV2Serializer(serializers.Serializer):

    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    place_description = serializers.CharField(
        max_length=250,
        allow_blank=False
    )

    def save(self):
        """
        Create location for user.
        """
        user = self.context.get('request').user
        validated_data = self.validated_data

        # Make point
        lat = validated_data['latitude']

        lng = validated_data['longitude']

        point = GEOSGeometry('SRID=4326;POINT({0} {1})'.format(lat, lng))
        place_description = validated_data.get(
            'place_description',
            'No description'
        )

        try:
            user.location_user.point = point
            user.location_user.place_description = place_description
            user.location_user.save()
            location_user = user.location_user
        except LocationUser.DoesNotExist:
            location_user = LocationUser.objects.create(user=user, point=point)
        return location_user


class SingleLocationV2Serializer(serializers.ModelSerializer):

    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    place_description = serializers.CharField(
        max_length=250,
        allow_blank=False
    )

    class Meta:
        model = LocationUser
        fields = (
            'id', 'latitude', 'longitude',
            'place_description'
        )

    def get_latitude(self, obj):
        return obj.point.get_x()

    def get_longitude(self, obj):
        return obj.point.get_y()


# Teacher Information


class UserTeacherDetailV2Serializer(serializers.ModelSerializer):

    sessions_as_a_teacher = serializers.SerializerMethodField()
    sessions_as_a_student = serializers.SerializerMethodField()
    rating_as_a_teacher = serializers.SerializerMethodField()
    rating_as_a_student = serializers.SerializerMethodField()
    price_per_hour = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'name',
            'last_name',
            'second_last_name',
            'description',
            'photo',
            'thumbnail',
            'email',
            'phone',
            'sessions_as_a_teacher',
            'sessions_as_a_student',
            'rating_as_a_teacher',
            'rating_as_a_student',
            'price_per_hour'
        )

    def get_sessions_as_a_teacher(self, instance):
        return instance.sessions_as_teacher

    def get_sessions_as_a_student(self, instance):
        return instance.sessions_as_student

    def get_rating_as_a_teacher(self, instance):
        return instance.get_rating_as_a_teacher()

    def get_rating_as_a_student(self, instance):
        return instance.get_rating_as_a_student()

    def get_price_per_hour(self, obj):
        subject_id = self.context.get('request').query_params.get('subject')
        return obj.price_per_hour(subject_id)


class LocationTeacherV2Serializer(serializers.ModelSerializer):

    user = UserTeacherDetailV2Serializer()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()

    class Meta:
        model = LocationUser
        fields = (
            'user',
            'place_description',
            'latitude',
            'longitude'
        )

    def get_latitude(self, obj):
        return obj.point.get_x()

    def get_longitude(self, obj):
        return obj.point.get_y()


class DeviceUserV2Serializer(serializers.ModelSerializer):

    class Meta:
        model = DeviceUser


class SearchFutureTeacherV2Serializer(serializers.Serializer):
    date = serializers.DateTimeField()
    teacher = UserTeacherDetailV2Serializer()
