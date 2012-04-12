from django.contrib.contenttypes.models import ContentType

from ostinato.pages.pages_registry import PageTemplate, page_templates


def get_template_choices():
    choices = []
    
    for template in page_templates.all():
        choices.append((template.template_id, template.description, template.order))

    return sorted(choices, key=lambda template: template[2])


def get_zones(page):
    zones = []
    page_template = PageTemplate.get_template_by_id(page.template)

    for index, zone in enumerate(page_template.zones):
        zone_id = zone[0]
        app_label = zone[1].split('.')[0]
        model = zone[1].split('.')[1]

        ct = ContentType.objects.get(app_label=app_label, model=model)
        instance, created = ct.model_class().objects.get_or_create(
            page=page, zone_id=zone_id)

        zones.append(instance)

    return zones

