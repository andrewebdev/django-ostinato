from django.views.generic import TemplateView
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings

from ostinato.models import ContentItem
from ostinato.models import OSTINATO_HOMEPAGE_SLUG, OSTINATO_PAGE_TEMPLATES
from ostinato.forms import ContentItemForm


class AjaxTemplateResponseMixin(object):
    template_name = None
    xhr_template_name = None

    def get_template_names(self):
        if self.request.is_ajax():
            self.template_name = self.xhr_template_name
        return super(AjaxTemplateResponseMixin, self).get_template_names()


class ContentItemDetail(AjaxTemplateResponseMixin, TemplateView):
	template_name = None
	xhr_template_name = None
	home = False

	def get_context_data(self, **kwargs):
		c = super(ContentItemDetail, self).get_context_data(**kwargs)
		if 'path' in kwargs:
			path = kwargs['path'].split('/')
			if not path[-1]:
				path = path[:-1]
			c['cms_item'] = get_object_or_404(ContentItem, slug=path[-1])
		else:
			# Use the home_page template
			c['cms_item'] = get_object_or_404(
				ContentItem, slug=OSTINATO_HOMEPAGE_SLUG)

		# Set the templates
		for template in OSTINATO_PAGE_TEMPLATES:
			if template['name'] == c['cms_item'].template:
				self.template_name = template['template']
				self.xhr_template_name = "xhr_%s" % self.template_name
				
		return c


class ContentItemEdit(AjaxTemplateResponseMixin, TemplateView):
	template_name = 'ostinato/contentitem_edit.html'
	xhr_template_name = 'ostinato/xhr_contentitem_edit.html'

	@method_decorator(permission_required('ostinato.change_contentitem'))
	def dispatch(self, *args, **kwargs):
		return super(ContentItemEdit, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		self.cms_item = ContentItem.objects.get(id=kwargs['id'])
		return super(ContentItemEdit, self).get_context_data(**kwargs)

	def get(self, *args, **kwargs):
		c = self.get_context_data(**kwargs)
		form = ContentItemForm(instance=self.cms_item)
		c['form'] = form
		return self.render_to_response(c)

	def post(self, *args, **kwargs):
		c = self.get_context_data(**kwargs)
		form = ContentItemForm(self.request.POST, instance=self.cms_item)
		if form.is_valid():
			self.cms_item = form.save()
			return HttpResponseRedirect(self.cms_item.get_absolute_url())
		c['form'] = form
		return self.render_to_response(c)