from django.contrib.contenttypes.models import ContentType
from django.conf import settings


OSTINATO_PAGE_TEMPLATES = getattr(settings, 'OSTINATO_PAGE_TEMPLATES')


for t in OSTINATO_PAGE_TEMPLATES:
    label, model = t[0].split('.')

    try:
        content_type = ContentType.objects.filter(app_label=label, model=model)
    except ContentType.DoesNotExist:
        raise Exception('OSTINATO_PAGE_TEMPLATES contains an invalid template'\
            ' identifier, "%s"''' % t[0])



