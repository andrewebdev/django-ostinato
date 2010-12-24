from django.db import models

class ContentItemManager(models.Manager):
    def _get_parents(self, item):
        if item.parent:
            yield item.parent
            self._get_parents(item.parent)

    def get_navbar(self, parent=None, depth=0):
        """
        Returns a dictionary of items with their titles and urls.

        ``parent`` is an instance of ContentItem. If specified, will only
        return items that has ``parent`` set as the ``parent`` for that item.

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

    def get_breadcrumbs(self, content_item):
        """
        Returns the breadcrumbs for the current ``content_item``
        The returned value is a list containing a dictionary for each
        item.

        """
        to_return = []
        parents = [parent for parent in self._get_parents(content_item)]
        if parents and not(None in parents):
            to_return += [{
                'title': parent.get_short_title(),
                'url': parent.get_absolute_url(),
                'current': False,
            } for parent in parents]
        to_return.append({
            'title': content_item.get_short_title(),
            'url': content_item.get_absolute_url(),
            'current': True,
        })
        return to_return
