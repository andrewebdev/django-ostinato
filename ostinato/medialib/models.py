from django.db import models
from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


conf = apps.get_app_config('ostinato_medialib')


class MediaItem(models.Model):
    """
    A single abstract media item which can belong to multiple libraries.
    """
    # Generic Relation Fields
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Media Item Meta fields
    title = models.CharField(max_length=200, null=True, blank=True)
    caption = models.CharField(max_length=500, null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=False)

    class Meta:
        abstract = True
        ordering = ('order',)

    def __unicode__(self):
        return self.title
