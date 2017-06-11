# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.staticfiles.templatetags.staticfiles import static

from .models import Class, ClassBill, Subject, Slot


class AdminSubject(admin.ModelAdmin):
    list_display = [
        'name',
        'description',
        'price_per_hour',
        'status',
        'university'
    ]

    search_fields = [
        'name',
        'status',
        'university__name'
    ]


class AdminClass(admin.ModelAdmin):
    list_display = [
        'student',
        'subject',
        'class_start_date',
        'promo_code',
        'class_status'
    ]

    search_fields = [
        'promo_code__code'
    ]

    readonly_fields = [
        'subject',
        'student',
        'teacher',
        'promo_code',
        'class_detail',
        'class_status',
        'meeting_now',
        'place_description',
        'participants',
        'time_zone_conf',
        'location',
        'class_end_date',
        'class_time',
        'class_start_date'
    ]


class AdminClassBill(admin.ModelAdmin):

    list_display = [
        'session',
        'teacher',
        'teacher_total',
        'created_at',
        'was_paid'
    ]

    search_fields = [
        'teacher',
        'session'
    ]

    readonly_fields = [
        'promo_code',
        'promo_discount_percentage',
        'session',
        'hourly_price',
        'total_hours',
        'commission',
        'commission_amount',
        'subtotal',
        'created_at',
        'was_paid',
    ]

    exclude = ('number_of_hours',)

    def promo_discount_percentage(self, obj):
        return obj.promo_code.discount


class AdminSlot(admin.ModelAdmin):

    class Media:
        css = {
            'all': (
                static('css/admin-reports.css'),
            )
        }

        js = (
            static('js/admin-reports.js'),
        )

    search_fields = [
     'teacher__username',
     'teacher__email'
    ]

    readonly_fields = [
        'teacher',
        'date',
        'start_time',
        'end_time',
        'is_unique',
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday',
        'sunday',
    ]


admin.site.register(Subject, AdminSubject)
admin.site.register(ClassBill, AdminClassBill)
admin.site.register(Class, AdminClass)
admin.site.register(Slot, AdminSlot)

