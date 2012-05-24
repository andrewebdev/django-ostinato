from django.contrib.contenttypes.models import ContentType
from django.db.utils import DatabaseError
from django.conf import settings


class InvalidTemplate(Exception):
    pass


class TemplateProcessor(object):
    """
    A class to validate and clean the OSTINATO_PAGE_TEMPLATES setting.
    """
    def __init__(self):
        self._templates = ()
        for t in getattr(settings, 'OSTINATO_PAGE_TEMPLATES'):
            template = (t[0].lower(), t[1])
            self.validate_template(template)
            self._templates += (template,)


    def get_templates(self):
        return self._templates


    def validate_template(self, template):
        label, model = template[0].lower().split('.')

        try:
            content_type = ContentType.objects.get(app_label=label, model=model)
        except ContentType.DoesNotExist:
            raise InvalidTemplate('OSTINATO_PAGE_TEMPLATES contains an invalid '
                'template id, "%s". Template id must be in the format '
                '"<app_label>.<model>"' % template[0])
        except DatabaseError:
            pass

        return (('.'.join([label, model]), template[1]),)

