from appregister import Registry


class PageTemplateRegistry(Registry):
    base = 'ostinato.pages.pages_registry.PageTemplate'
    discovermodule = 'pages_registry'


page_templates = PageTemplateRegistry()


class PageTemplate(object):
    """
    The parent class for all Page Templates. You need to define the following
    attributes in your templates.

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
    template_id = None  # A unique string id for the template
    description = None  # A short description for the template
    template = None  # The location where the actual django template is located
    zones = None  # A tuple of tuples containing the zone_id and model

    @classmethod
    def get_template_by_id(cls, template_id):
        """ Looks through the registry for 'template_id' """
        for template in page_templates.all():
            if template.template_id == template_id:
                return template
        # TODO: should raise an exception if zone isn't found

