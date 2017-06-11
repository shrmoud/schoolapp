# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView

from tandlr.registration.views import confirm

admin.autodiscover()

"""
API REST VERSION v1
"""

urlpatterns = [
    url(
        r'^api/',
        include(
            'tandlr.api.urls',
            namespace='api'
        )
    ),
    url(r'^confirm/(?P<activation_key>\w+)/$',
        confirm,
        name='registration_confirm'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin_tools/', include('admin_tools.urls')),
] + static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)

if 'tandlr.emails' in settings.INSTALLED_APPS and settings.TEMPLATE_DEBUG:
    urlpatterns = urlpatterns + patterns(
        '',
        url(r'^email-preview/',
            include('tandlr.emails.urls', namespace='emails'))
    )

if True:
    # This URL is only to test the sockets. Remove after that the sockets are
    # added in the frontend.
    urlpatterns += [
        url(
            r'^notifications$',
            TemplateView.as_view(
                template_name="notifications/test_sockets.html"
            ),
            name='notifications_example'
        ),
    ]
