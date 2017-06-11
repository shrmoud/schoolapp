# -*- coding: utf-8 -*-
from django.conf.urls import url

from tandlr.api.autodiscover import autodiscover

from .routers import router

autodiscover()

urlpatterns = router.urls + [
    url(
        r'^auth/token-refresh',
        'rest_framework_jwt.views.refresh_jwt_token',
        name='auth-token-refresh'
    ),
    url(
        r'^auth/token-verify',
        'rest_framework_jwt.views.verify_jwt_token',
        name='auth-token-verify'
    ),
]
