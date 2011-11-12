from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from ostinato.models import ContentItem

try:
    from django.dispatch import receiver # django 1.3
except ImportError:
    receiver = None


def create_contentitem(sender, **kwargs):
    instance = kwargs['instance']
    content_type = ContentType.objects.get_for_model(instance)
    title = getattr(instance, 'title', repr(instance))
    content_item, created = ContentItem.objects.get_or_create(
        content_type=content_type, object_id=instance.id)
    if created:
        content_item.title = title
        content_item.save()


class OstinatoCMS(object):
    @classmethod
    def register(cls, model):
        """
        Register a model with Ostinato. The registration will do the
        following:
            - create a ContentItem instance automatically when the
            model is saved
        """
        # Connect the post_save signal for the model
        global create_contentitem
        if receiver:
            create_contentitem = receiver(post_save,
                sender=model)(create_contentitem)
        else:
            post_save.connect(create_contentitem, sender=model)

    @classmethod
    def unregister(cls, model):
        """ Unregister a model from Ostinato. """
        # Disconnect any signal handlers
        global create_contentitem
        post_save.disconnect(create_contentitem, sender=model)


def register_apps():
    """
    Cycle through all the models in Settings, and register them with
    ostinato.
    """
    OSTINATO_APP_MODELS = getattr(settings, 'OSTINATO_MODELS',
        ('ostinato.basicpage',))
    for app_model in OSTINATO_APP_MODELS:
        app, model_name = app_model.split('.')
        ct = ContentType.objects.get(app_label=app, model=model_name)
        OstinatoCMS.register(ct.model_class())