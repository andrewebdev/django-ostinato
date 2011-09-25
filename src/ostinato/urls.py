from django.conf.urls.defaults import patterns, include, url

from ostinato.core import OstinatoCMS
from ostinato.views import ContentItemDetail, ContentItemEdit
from ostinato.models import BasicPage

urlpatterns = patterns('',
	url(r'^$', ContentItemDetail.as_view(), name="ostinato_home"),

    url(r'^edit/(?P<slug>[-\w]+)/$', ContentItemEdit.as_view(),
        name="ostinato_contentitem_edit"),
	
	# This must be last
	url(r'^(?P<path>.*)$', ContentItemDetail.as_view(),
		name="ostinato_contentitem_detail"),
)

OstinatoCMS.register(BasicPage)