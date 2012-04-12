from appregister import Registry


class PageTemplateRegistry(Registry):
    base = 'ostinato.pages.pages_registry.PageTemplate'
    discovermodule = 'pages_registry'


page_templates = PageTemplateRegistry()


class PageTemplate(object):
    """
    The parent class for all Page Templates. You need to define the following
    attributes in your templates.

    ``order``: a unique number that specifies the ordering of the templates
    ``template_id``: a unique string id for the template
    ``description``: a short description for the template
    ``template``: the location where the django html template is located
    ``zones``: a tuple of tuples containing the zone_id and model

        zones = (

            ('example', 'app.model'),
            ('misc', 'app.model'),

            ... etc ...
        )

    """
    order = 0
    template_id = None
    description = None
    template = None
    zones = None

    @classmethod
    def get_template_by_id(cls, template_id):
        """ Looks through the registry for 'template_id' """
        for template in page_templates.all():
            if template.template_id == template_id:
                return template
        # TODO: should raise an exception if zone isn't found

