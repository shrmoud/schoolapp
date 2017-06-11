from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'^(?P<page>[a-zA-Z_/.-]+)$',
        views.StaticEmailView.as_view(), name='email')
)
