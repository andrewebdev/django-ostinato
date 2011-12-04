from django.db import models
from django.contrib.contenttypes.models import ContentType


class ContentItemManager(models.Manager):

    def create_for(self, object_instance, **kwargs):
        """
        A custom create method which will create a new ContentItem,
        that will point directly to another ContentType.

        ``object_instance`` will be the item we wish to create a new
        ContentItem instance for.

        Once created return the instance of the new content_item.
        """
        ctype = ContentType.objects.get_for_model(object_instance)
        content_item = self.get_query_set().create(
            content_type=ctype, object_id=object_instance.id, **kwargs)
        content_item.save()
        return content_item

    def get_for(self, object_instance):
        """ Returns the ContentItem instance for ``object_instance`` """
        ctype = ContentType.objects.get_for_model(object_instance)
        return self.get_query_set().get(
            content_type=ctype, object_id=object_instance.id)

    def get_navbar(self, parent=None):
        """
        Returns a dictionary of items with their titles and urls.

        ``parent`` is an instance of ContentItem. If specified, will only
        return items that has ``parent`` set as the ``parent`` for that
        item.
        """
        to_return = []
        nav_items = self.get_query_set().filter(parent=parent, show_in_nav=True)
        if nav_items:
            for item in nav_items:
                to_return.append({
                    'title': item.get_short_title(),
                    'url': item.get_absolute_url(),
                })
        return to_return

