import re
from appregister import SortedRegistry


class TemplateRegistry(SortedRegistry):
    base = 'ostinato.pages.registry.PageTemplate'
    discovermodule = 'page_templates'

    def get_template(self, template_id):
        for template in self.all():
            if template_id == template.__name__.lower():
                return template

    def get_template_choices(self):
        template_choices = (('', '--------'),)

        for template in self.all():
            template_id = template.__name__.lower()
            template_choices += ((template_id, template.get_verbose_name()),)

        return template_choices

    def get_template_name(self, template_id):
        choices = self.get_template_choices()

        for c in choices:
            if c[0] == template_id:
                return c[1]

        return template_id


# Create the base PageContent object
class PageTemplate(object):
    """
    ``template`` is the template path relative the templatedirs.
    ``view`` is a custom view that will handle the rendering for the page.
    ``form`` a custom form to use in the admin.
    """
    template = None
    view = 'ostinato.pages.views.PageView'
    form = None
    page_content = []  # List of models to be included
    # admin_inlines = []

    @classmethod
    def get_template(cls):
        if cls.template:
            return cls.template

        cls_name = re.findall('[A-Z][^A-Z]*', cls.__name__)
        template = 'pages/%s.html' % '_'.join([i.lower() for i in cls_name])
        return template
    template_name = property(get_template)

    @classmethod
    def get_verbose_name(cls):
        if hasattr(cls, 'verbose_name'):
            return cls.verbose_name
        cls_name = re.findall('[A-Z][^A-Z]*', cls.__name__)
        return ' '.join(cls_name)

page_templates = TemplateRegistry()
