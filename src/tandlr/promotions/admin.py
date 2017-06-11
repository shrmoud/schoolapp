# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html


from tandlr.promotions.models import BatchPromotionCode, PromotionCode

from .forms import BatchPromotionCodeForm


@admin.register(PromotionCode)
class AdminPromotionCode(admin.ModelAdmin):
    list_display = [
        'expiration_date',
        'code',
        'discount_percentage',
        'is_active',
        'uses_per_user'
    ]

    readonly_fields = [
        'is_active',
    ]

    search_fields = [
        'code',
    ]


@admin.register(BatchPromotionCode)
class AdminBatchPromotionCode(admin.ModelAdmin):
    list_display = [
        'number',
        'expiration_date',
        'discount_percentage'
    ]
    form = BatchPromotionCodeForm

    def save_model(self, request, obj, form, change):
        messages.info(
            request,
            format_html(
                'The batch process has completed successfully, '
                'please proceed to the '
                '<a href="/admin/promotions/promotioncode/">{}</a> '
                'to view them.',
                'Code list section'
            )
        )
        super(AdminBatchPromotionCode, self).save_model(
            request, obj, form, change
        )
