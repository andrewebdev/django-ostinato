from django.conf.urls import url
from ostinato.statemachine.views import StateActionView


urlpatterns = [
    url(r'^(?P<app_label>\w+)/(?P<model>\w+)/(?P<obj_id>\d+)/$',
        StateActionView.as_view(), name='statemachine_action'),
]

