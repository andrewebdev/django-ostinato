from django.views.generic import TemplateView

from ostinato.models import ContentItem
from ostinato.forms import ContentItemForm

class AjaxTemplateResponseMixin(object):
    template_name = None
    xhr_template_name = None

    def get_template_names(self):
        if self.request.is_ajax():
            self.template_name = self.xhr_template_name
        return super(AjaxTemplateResponseMixin, self).get_template_names()


class ContentItemEdit(AjaxTemplateResponseMixin, TemplateView):
	template_name = 'ostinato/contentitem_edit.html'
	xhr_template_name = 'ostinato/xhr_contentitem_edit.html'

	## TODO: Two required decorators
	# 1. login_required
	# 2. can_edit permission
	def dispatch(self, *args, **kwargs):
		self.cms_item = ContentItem.objects.get(id=kwargs['id'])
		return super(ContentItemEdit, self).dispatch(*args, **kwargs)

	def get(self, *args, **kwargs):
		c = self.get_context_data(**kwargs)
		c['form'] = ContentItemForm(instance=self.cms_item)
		return self.render_to_response(c)