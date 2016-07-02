import uuid
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from . import CONTENTBROWSER
from .core import get_browsers


class CBWidgetMixin(object):

    def render(self, name, value, attrs=None, **kwargs):
        """
        Render the original field, but append our browser to the output
        """
        rendered = super(CBWidgetMixin, self).render(name, value, attrs)
        browsers = get_browsers()
        widget_id = uuid.uuid1()
        context = {
            'browsers': browsers,
            'widget_id': widget_id,
            'actions_script': CONTENTBROWSER['actions_script'],
            'field_name': name,
        }
        return rendered + mark_safe(
            render_to_string('contentbrowser/widgets/_contentbrowser.html',
                             context))
