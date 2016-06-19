from django import http

from ostinato.pages.views import PageView


# Set up some custom views
class CustomView(PageView):

    def get_context_data(self, **kwargs):
        c = super(CustomView, self).get_context_data(**kwargs)
        c['custom'] = 'Some Custom Context'
        return c


def functionview(request, *args, **kwargs):
    return http.HttpResponse('ok')

