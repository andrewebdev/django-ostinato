from django.conf.urls.defaults import patterns, include, url

from ostinato.core import OstinatoCMS
from ostinato.views import ContentItemDetail, ContentItemEdit
from ostinato.models import BasicPage

urlpatterns = patterns('',
	url(r'^$', ContentItemDetail.as_view(), name="ostinato_home"),
	
	url(r'^(?P<path>.*)$', ContentItemDetail.as_view(),
		name="ostinato_contentitem_detail"),

    # url(r'^contentitem/edit/(?P<id>\d+)/$', ContentItemEdit.as_view(),
    #     name="ostinato_contentitem_edit"),
)

OstinatoCMS.register(BasicPage)