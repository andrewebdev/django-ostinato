from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType

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
        title=title,
        content_type=content_type,
        object_id=instance.id,
    )

class OstinatoCMS(object):
    @classmethod
    def register(cls, model):
        """
        Register a model with Ostinato. The registration will do the following:
            - create a ContentItem instance automatically when the model is saved
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
