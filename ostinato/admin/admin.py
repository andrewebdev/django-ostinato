from django.contrib import admin
from django.urls import path


class OstinatoModelAdmin(admin.ModelAdmin):
    """
    ModelAdmin customizations that provides a couple of nice extras that we
    often need.
    """

    """
    Custom Object Tools
    -----------------------
    ``changelist_tools`` - List of tuples containing, in order:

    1. Button text as string
    2. Django url path string, relative to the current admin view url
    3. The view method name to call for the request, eg:

    **Example Usage:**

    .. code::

        changelist_tools = (
            ('Test Message', 'test/', 'test_message'),
        )

        def test_message(self, request):
            self.message_user(request, 'test message!')
            return http.HttpResponseRedirect('../')
    """
    changelist_tools = None

    def get_urls(self):
        urls = super().get_urls()
        tool_urls = [
            path(pattern, getattr(self, view))
            for _, pattern, view in self.changelist_tools
        ]
        return tool_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        if self.changelist_tools:
            extra_context['changelist_tools'] = self.changelist_tools
        return super().changelist_view(request, extra_context=extra_context)
