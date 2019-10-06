from urllib.parse import urlparse
from django import http
from django.conf import settings
from .models import Redirect


def redirect_middleware(get_response):

    def middleware(request):
        response = get_response(request)
        if response.status_code != 404:
            return response
            # No need to check for a redirect for non-404 responses.

        full_path = request.get_full_path()
        if settings.APPEND_SLASH and not full_path.endswith('/'):
            full_path = "{}/".format(full_path)

        req_url = urlparse(full_path)

        redirect = None
        try:
            redirect = Redirect.objects.get(old_path=req_url.path)
        except Redirect.DoesNotExist:
            return response

        if redirect.code == 410:
            return http.HttpResponseGone()

        if redirect.code == 301:
            return http.HttpResponsePermanentRedirect(redirect.new_path)

        return http.HttpResponseRedirect(redirect.new_path)

    return middleware
