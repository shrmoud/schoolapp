# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import glob
import os

from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from pyexcel.cookbook import merge_all_to_a_book

import unicodecsv

from tandlr.celery import app
from tandlr.users.models import Teacher


@app.task
def unpaid_session_sales():
    """
    The first report will list the total of class bills that have not been
    paid in the last 15 days
    """
    yesterday = timezone.now() - timedelta(days=1)
    report_timespan = yesterday - timedelta(days=settings.REPORT_TIMESPAN)

    teachers = Teacher.objects.filter(
        class_teacher__bills__created_at__gte=report_timespan,
        class_teacher__bills__was_paid=False,
        class_teacher__class_status__id__in=[
            3, # Accepted
            4, # On Course
            5  # Finished
        ]
    ).order_by('email').distinct()

    first_report_headers = [
        'Name',
        'Email',
        'Number of bills',
        'Total'
    ]

    second_report_headers = [
        'Name',
        'Email',
        'Created at',
        'Number of hours',
        'Hourly price',
        'Total'
    ]

    first_report_filename = os.path.join(
        settings.REPORTS_ROOT,
        'consolidated_{year}_{month}_{day}.csv'.format(
            year=yesterday.year,
            month=yesterday.month,
            day=yesterday.day
        )
    )

    second_report_filename = os.path.join(
        settings.REPORTS_ROOT,
        'detailed_{year}_{month}_{day}.csv'.format(
            year=yesterday.year,
            month=yesterday.month,
            day=yesterday.day
        )
    )

    first_report_rows = []
    second_report_rows = []

    with open(first_report_filename, 'w') as csv_file:

        writer = unicodecsv.writer(csv_file, encoding='utf-8')
        writer.writerow(first_report_headers)

        for teacher in teachers:
            total = 0
            number_of_bills = 0

            sessions = teacher.class_teacher.filter(
                bills__created_at__gte=report_timespan,
                bills__was_paid=False,
                class_status__id__in=[
                    3, # Accepted
                    4, # On Course
                    5  # Finished
                ]
            ).distinct()

            for session in sessions:
                bills = session.bills.filter(
                    created_at__gte=report_timespan,
                    was_paid=False
                ).distinct()

                total += sum([bill.teacher_total for bill in bills])
                number_of_bills += bills.count()

            row = [
                teacher.get_full_name(),
                teacher.email,
                number_of_bills,
                total
            ]

            writer.writerow(row)
            first_report_rows.append(row)

    with open(second_report_filename, 'w') as csv_file:

        writer = unicodecsv.writer(csv_file, encoding='utf-8')
        writer.writerow(second_report_headers)

        for teacher in teachers:
            sessions = teacher.class_teacher.filter(
                bills__created_at__gte=report_timespan,
                bills__was_paid=False,
                class_status__id__in=[
                    3, # Accepted
                    4, # On Course
                    5  # Finished
                ]
            ).distinct()

            for session in sessions:
                for bill in session.bills.filter(
                    created_at__gte=report_timespan,
                    was_paid=False
                ).distinct():

                    row = [
                        teacher.get_full_name(),
                        teacher.email,
                        bill.created_at,
                        bill.duration,
                        bill.hourly_price,
                        bill.teacher_total
                    ]

                    writer.writerow(row)
                    second_report_rows.append(row)

                    bill.was_paid = True
                    bill.save()

    #
    # Create an email with the report appended to it
    #

    email_context = {
        'yesterday': yesterday,
        'report_timespan': report_timespan,
        'first_report_headers': first_report_headers,
        'second_report_headers': second_report_headers,
        'first_report_rows': first_report_rows,
        'second_report_rows': second_report_rows
    }

    template_names = (
        'email/reports/reports_subject.txt',
        'email/reports/reports.txt',
        'email/reports/reports.html'
    )

    subject, body, html = map(
        lambda t: render_to_string(t, email_context),
        template_names
    )

    msg_report = EmailMultiAlternatives(
        subject=''.join(subject.splitlines()),
        body=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=settings.REPORT_EMAILS,
        bcc=settings.BCC_REPORT_EMAILS
    )

    #
    # Create the xlsx files
    #

    first_report_filename_xlsx = os.path.join(
        settings.REPORTS_ROOT,
        'consolidated_{year}_{month}_{day}.xlsx'.format(
            year=yesterday.year,
            month=yesterday.month,
            day=yesterday.day
        )
    )

    merge_all_to_a_book(
        glob.glob(first_report_filename),
        first_report_filename_xlsx
    )

    second_report_filename_xlsx = os.path.join(
        settings.REPORTS_ROOT,
        'detailed_{year}_{month}_{day}.xlsx'.format(
            year=yesterday.year,
            month=yesterday.month,
            day=yesterday.day
        )
    )

    merge_all_to_a_book(
        glob.glob(second_report_filename),
        second_report_filename_xlsx
    )

    msg_report.attach_alternative(html, 'text/html')
    msg_report.attach_file(first_report_filename_xlsx)
    msg_report.attach_file(second_report_filename_xlsx)
    msg_report.send()
