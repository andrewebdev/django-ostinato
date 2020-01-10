from django.views.generic import TemplateView
from django.conf import settings


class OstinatoEditorView(TemplateView):
    template_name = 'ostinato/ostinato_editor_frame.html'

    def get_context_data(self, **kwargs):
        c = super().get_context_data(**kwargs)
        # TODO: Allow for override of this import path
        c['editorjs_import'] = '{}ostinato/node_modules/@editorjs/editorjs/dist/editor.js'.format(
            settings.STATIC_URL)
        return c
