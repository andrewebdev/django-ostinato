from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView


urlpatterns = patterns('',
    ## Just create a dummy url to be used with the tests
    url(r'^with/sub/path/$', TemplateView.as_view(
        template_name='pages/tests/basic_page.html'), name='sub_url_name'),
)