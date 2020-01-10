from django import forms
from django.utils.encoding import force_text
from django.conf import settings


OSTINATO_EDITOR_PATH = getattr(
    settings,
    'OSTINATO_EDITOR_PATH',
    '{}ostinato/dist/ostinato-editor.js'.format(settings.STATIC_URL))

DEFAULT_CONFIG_MODULE = getattr(
    settings,
    'OSTINATO_EDITOR_CONFIG_MODULE',
    '{}ostinato/src/basic_editor.js'.format(settings.STATIC_URL))


class EditorJSWidget(forms.Textarea):
    template_name = 'ostinato/admin/widget_editorjs.html'

    class Media:
        js = (
            OSTINATO_EDITOR_PATH,
        )

    def __init__(self, attrs=None, config_module=None):
        """
        The config module is a a javascript module path, that must contain
        a constant named: `editorConfig`. This will be the standard config
        format for EditorJS.
        If this is not supplied, we will fall back to a default.
        """
        super().__init__(attrs)
        if config_module is None:
            config_module = DEFAULT_CONFIG_MODULE
        self.config_module = config_module

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ''
        value = force_text(value)

        final_attrs = self.build_attrs(self.attrs, attrs)
        final_attrs['name'] = name

        if final_attrs.get('class', None) is None:
            final_attrs['class'] = 'editorjs'
        else:
            final_attrs['class'] = ' '.join(
                final_attrs['class'].split(' ') + ['editorjs'])

        context = self.get_context(name, value, attrs)
        context['editor_uuid'] = '_editor-{}'.format(name)
        context['config_module'] = self.config_module

        return self._render(self.template_name, context)
