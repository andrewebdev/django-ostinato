import json
from django import http
from django.core.serializers.json import DjangoJSONEncoder


class AjaxTemplateResponseMixin(object):
    template_name = None
    xhr_template_name = None

    def get_template_names(self):
        if self.request.is_ajax():
            self.template_name = self.xhr_template_name
        return super(AjaxTemplateResponseMixin, self).get_template_names()


class JsonResponseMixin(object):

    def render_json_response(self, data, **kwargs):
        # Note the use of the DjangoJSONEncoder here, this handles date/time
        # and Decimal values correctly
        data = json.dumps(data, cls=DjangoJSONEncoder)
        return http.HttpResponse(
            data, content_type='application/json; charset=utf-8')
