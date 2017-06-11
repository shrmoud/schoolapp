# -*- coding: utf-8 -*-
from django.conf import settings
from django.conf.urls import include, patterns, url


urlpatterns = patterns(
    '',
    url(
        r'^v1/',
        include(
            'tandlr.api.v1.urls',
            namespace='v1'
        )
    ),
    url(
        r'^v2/',
        include(
            'tandlr.api.v2.urls',
            namespace='v2'
        )
    ),
)


if not settings.PRODUCTION:
    urlpatterns += patterns(
        '',
        url(
            r'^docs/',
            include('rest_framework_swagger.urls')
        ),
    )
