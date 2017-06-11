# -*- coding: utf-8 -*-
from django.conf.urls import include, patterns, url

from tandlr.authentication.viewsets import LoginViewSet, LogoutViewSet

from tandlr.core.api import routers

from tandlr.feedbacks.viewsets import (
    FeedbackDetailRatesByStudentViewSet,
    FeedbackDetailRatesByTeacherViewSet,
    FeedbackFullViewSet,
    FeedbackViewSet
)

from tandlr.logs.viewsets import (
    LogMailViewSet,
    LogbookUserViewSet
)

from tandlr.notifications.viewsets import NotificationViewSet

from tandlr.registration.viewsets import (
    ChangePasswordViewSet,
    NewPasswordViewSet,
    RegistrationProfileViewSet,
    ResetTokenViewSet
)

from tandlr.scheduled_classes.viewsets import (
    ClassFilterViewSet,
    ClassStatusViewSet,
    ClassViewSet,
    RequestClassExtensionTimeFilterViewSet,
    RequestClassExtensionTimeViewSet,
    SubjectTeacherViewSet,
    SubjectViewSet
)

from tandlr.security_configuration.viewsets import (
    PermissionRoleViewSet,
    PermissionViewSet,
    RoleUserViewSet,
    RoleViewSet
)

from tandlr.stripe.viewsets import (
    StripeCardViewSet,
    StripeChargeViewSet,
    StripeCustomerViewSet
)

from tandlr.users.viewsets import (
    DeviceUserViewSet,
    LocationUserViewSet,
    TeachersByLocationViewSet,
    UserFilterViewSet,
    UserLoggedViewSet,
    UserSettingsFilterViewSet,
    UserSettingsViewSet,
    UserViewSet
)

router = routers.SimpleRouter()


"""
API REST VERSION v1
"""

"""
Authentication
"""

router.register(r'login', LoginViewSet, base_name="login")
router.register(r'logout', LogoutViewSet, base_name="logout")

router.register(r'register', RegistrationProfileViewSet, base_name="register")

router.register(
    r'new-passwords',
    NewPasswordViewSet,
    base_name='reset_password'
)
router.register(
    r'change-passwords',
    ChangePasswordViewSet,
    base_name='change_password'
)


"""
Logs
"""
router.register(r'loogbook-user', LogbookUserViewSet)

router.register(r'log-mail', LogMailViewSet)


"""
Notifications
"""
router.register(
    r'notifications',
    NotificationViewSet,
    base_name='notification'
)


"""
Rates ( Base Feedbacks )
"""
router.register(r'rates-teacher',
                FeedbackDetailRatesByTeacherViewSet)

router.register(r'rates-student',
                FeedbackDetailRatesByStudentViewSet)

"""
Security configuration
"""
router.register(r'role', RoleViewSet)

router.register(r'role-user', RoleUserViewSet, base_name='role-user')

router.register(r'permission', PermissionViewSet)

router.register(r'permission-role', PermissionRoleViewSet)

"""
Users
"""
router.register(r'user', UserViewSet, base_name='user')

router.register(r'user-filter', UserFilterViewSet, base_name='user-filter')

router.register(r'user-logged', UserLoggedViewSet)

router.register(r'user-settings', UserSettingsViewSet)

router.register(r'user-settings-filter', UserSettingsFilterViewSet)

router.register(r'location-user', LocationUserViewSet,
                base_name='location-user')

router.register(r'device-user', DeviceUserViewSet)

"""
Get  teacher by location and subject
"""
router.register(r'teachers-by-location-and-subject', TeachersByLocationViewSet)

"""
Feedbacks
"""
router.register(r'feedback', FeedbackViewSet)

router.register(r'feedback-filter', FeedbackFullViewSet)

"""
Logs
"""
router.register(r'loogbook-user', LogbookUserViewSet)

router.register(r'log-mail', LogMailViewSet)


"""
Schedule classes
"""
router.register(r'subject', SubjectViewSet)

router.register(r'subject-teacher', SubjectTeacherViewSet)

router.register(r'class-status', ClassStatusViewSet)

router.register(r'class', ClassViewSet, base_name='class')

router.register(r'class-filter', ClassFilterViewSet, base_name='class-filter')

router.register(
    r'request-class-extension-time',
    RequestClassExtensionTimeViewSet,
    base_name='request-class-extension-time'
)

router.register(
    r'request-class-extension-time-filter',
    RequestClassExtensionTimeFilterViewSet,
    base_name='request-class-extension-time-filter'
)

router.register(
    r'stripe-charges',
    StripeChargeViewSet,
    base_name='stripe-charges'
)

router.register(
    r'stripe-customers',
    StripeCustomerViewSet,
    base_name='stripe-customers'
)

router.register(
    r'stripe-cards',
    StripeCardViewSet,
    base_name='stripe-cards'
)

urlpatterns = patterns(
    '',

    url(r'', include(router.urls)),

    url(
        r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')
    ),

    url(
        r'^api-token-refresh/',
        ResetTokenViewSet.as_view()
    ),

    url(
        r'^api-token-verify/',
        'rest_framework_jwt.views.verify_jwt_token'
    ),
)
