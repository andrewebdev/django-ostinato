from django.contrib.contenttypes.models import ContentType
from django.conf import settings


def filter_templates():
    """
    A utility method to filter templates
    """

    ## The following is an example of how we can set up a Queryset limiter
    limit = models.Q(app_label='app', model='a') |\
        models.Q(app_label='app', model='b') |\
        models.Q(app_label='app2', model='c') 

    return limit
