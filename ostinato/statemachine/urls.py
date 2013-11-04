from django.conf.urls import patterns, url
from ostinato.statemachine.views import StateActionView


urlpatterns = patterns('',
    url(r'^(?P<app_label>\w+)/(?P<model>\w+)/(?P<obj_id>\d+)/$',
        StateActionView.as_view(), name='statemachine_action'),
)
