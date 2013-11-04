from django import http
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import View


class TestView(View):
    def get(self, *args, **kwargs):
        return http.HttpResponse('ok')


urlpatterns = patterns('',
    url(r'^$', TestView.as_view()),
    url(r'^', include('ostinato.statemachine.urls')),
)
