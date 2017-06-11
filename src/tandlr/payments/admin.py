# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import (
    Currency,
    PaymentMethod,
    StatusPayment,
    TeacherPaymentInformation,
    TypeCard,
    TypePayment,
)


class AdminTypeCard(admin.ModelAdmin):
    list_display = [
        'name',
        'status'
    ]

    search_fields = [
        'name',
    ]


class AdminCurrency(admin.ModelAdmin):
    list_display = [
        'symbol',
        'code',
        'status'
    ]

    search_fields = [
        'code',
        'symbol'
    ]


class AdminStatusPayment(admin.ModelAdmin):
    list_display = [
        'name',
        'description',
        'status'
    ]

    search_fields = [
        'name',
        'description',
    ]


class AdminTypePayment(admin.ModelAdmin):
    list_display = [
        'name',
        'description',
        'status'
    ]

    search_fields = [
        'name',
        'description',
    ]


class AdminPaymentMethod(admin.ModelAdmin):
    list_display = [
        'name',
        'description',
        'status'
    ]

    search_fields = [
        'name',
        'description',
    ]


class AdminTeacherPaymentInformation(admin.ModelAdmin):

    raw_id_fields = [
        'teacher'
    ]

    list_display = [
        'teacher',
        'bank',
        'account_number',
        'social_security_number'
    ]

    search_fields = [
        'bank',
        'account_number',
        'social_security_number'
    ]

admin.site.register(TypeCard, AdminTypeCard)
admin.site.register(Currency, AdminCurrency)
admin.site.register(StatusPayment, AdminStatusPayment)
admin.site.register(TypePayment, AdminTypePayment)
admin.site.register(PaymentMethod, AdminPaymentMethod)
admin.site.register(TeacherPaymentInformation, AdminTeacherPaymentInformation)
