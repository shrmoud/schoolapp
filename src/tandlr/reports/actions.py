# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.utils import timezone

import unicodecsv as csv


def export_as_csv(modeladmin, request, queryset):
    """
    function that dynamically creates CSV.
    """
    now = timezone.now().strftime('%Y-%m-%d %H:%M')

    fields = modeladmin.model().get_fields_report

    file_name = modeladmin.model().get_name_report

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.csv' % (
        file_name + '_' + now
    )

    writer = csv.writer(response)
    writer.writerow(fields)

    for item in queryset:
        writer.writerow([getattr(item, field) for field in fields])

    return response

export_as_csv.short_description = "Export to CSV"
