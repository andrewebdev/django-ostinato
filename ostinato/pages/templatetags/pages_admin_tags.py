from django import template
from django.conf import settings

import mptt.templatetags.mptt_admin as mptt


register = template.Library()


@register.inclusion_tag('admin/mptt_change_list_results.html')
def pages_result_list(cl):
    """
    Displays the headers and data list together
    """
    return {'cl': cl,
            'is_grappelli': 'grappelli' in settings.INSTALLED_APPS,
            'result_hidden_fields': list(mptt.result_hidden_fields(cl)),
            'result_headers': list(mptt.result_headers(cl)),
            'results': list(mptt.mptt_results(cl))}

