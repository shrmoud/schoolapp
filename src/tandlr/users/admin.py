# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext_lazy as _

from tandlr.scheduled_classes.models import Subject, SubjectTeacher

from .models import Student, Teacher, User


class SubjectTeacherInline(admin.StackedInline):
    model = SubjectTeacher
    extra = 1

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(SubjectTeacherInline, self).get_formset(
            request, obj, **kwargs
        )

        #
        # Checks the parent user information, based in request information,
        # This code should be applied only if isn't a creation.
        #
        if request.resolver_match.args:
            parent_id = request.resolver_match.args[0]

            user_model = get_user_model()
            parent_user = user_model.objects.get(id=parent_id)

            formset.form.base_fields[
                'subject'
            ].queryset = Subject.objects.filter(
                university=parent_user.university
            )
        return formset


class UserAdmin(BaseUserAdmin):
    """
    Custom admin for the tandlr users model.
    """
    ordering = ['email', ]

    search_fields = [
        'name',
        'email',
        'last_name',
        'second_last_name',
        'phone',
    ]

    list_display = [
        'email',
        'full_name',
        'phone',
        'birthday',
        'gender',
        'is_active',
        'is_student',
        'is_teacher',
        'is_available',
        'customer_id',
    ]

    list_filter = [
        'gender',
        'is_active',
        'is_student',
        'is_teacher',
        'settings__available',
    ]

    fieldsets = (
        (None, {'fields': (
            'email', 'username', 'password', 'gender',
        )}),
        (_('Personal info'), {'fields': (
            'name', 'last_name', 'second_last_name'
        )}),
        (_('Permissions'), {'fields': (
            'is_active', 'is_staff', 'is_superuser',
            'is_teacher', 'is_student',
            'groups',
        )}),
        (_('Important dates'), {'fields': (
            'last_login', 'register_date', 'last_modify_date'
        )}),
        (_('University'), {'fields': (
            'university',
        )}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2')
        }),
    )

    readonly_fields = ('register_date', 'last_modify_date', 'last_login')

    inlines = [SubjectTeacherInline, ]

    def full_name(self, instance):
        return instance.get_full_name()

    def is_available(self, instance):
        return instance.settings.available

    is_available.boolean = True


class TeacherAdmin(UserAdmin):
    """
    Admin created to show users, filtered by teachers, also showing them rates.
    """
    list_display = [
        'email',
        'full_name',
        'is_active',
        'customer_id',
        'sessions_as_teacher',
        'get_rating_as_a_teacher_admin',
        'university'
    ]

    def get_queryset(self, request):
        queryset = super(TeacherAdmin, self).get_queryset(request)
        return queryset.filter(is_teacher=True)

    def full_name(self, instance):
        return instance.get_full_name()

    def teacher_average(self, instance):
        return instance.user_summary.score_average_teacher

    def student_average(self, instance):
        return instance.user_summary.score_average_student

    def get_rating_as_a_teacher_admin(self, instance):
        return instance.get_rating_as_a_teacher()

    student_average.admin_order_field = 'user_summary__score_average_student'
    teacher_average.admin_order_field = 'user_summary__score_average_teacher'
    get_rating_as_a_teacher_admin.short_description = 'Rating as a teacher'


class StudentAdmin(UserAdmin):
    """
    Admin created to show users, filtered by students, also showing them rates.
    """
    list_display = [
        'email',
        'full_name',
        'is_active',
        'customer_id',
        'sessions_as_student',
        'get_rating_as_a_student_admin'
    ]

    def get_queryset(self, request):
        queryset = super(StudentAdmin, self).get_queryset(request)
        return queryset.filter(is_teacher=False, is_student=True)

    def full_name(self, instance):
        return instance.get_full_name()

    def average(self, instance):
        return instance.user_summary.score_average_student

    def get_rating_as_a_student_admin(self, instance):
        return instance.get_rating_as_a_student()

    average.admin_order_field = 'user_summary__score_average_student'
    get_rating_as_a_student_admin.short_description = 'Rating as a student'


admin.site.register(User, UserAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Student, StudentAdmin)
