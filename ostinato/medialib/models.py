from django.db import models
from django.apps import apps
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


conf = apps.get_app_config('ostinato_medialib')


class MediaItemManager(models.Manager):

    def visible(self):
        return self.get_queryset().filter(is_visible=True)


class MediaItem(models.Model):
    """
    A single abstract media item which can be attached to any other
    content type
    """
    content_type = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Media Item Meta fields
    title = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=500, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_visible = models.BooleanField(default=False)

    objects = MediaItemManager()

    class Meta:
        abstract = True
        ordering = ('order',)

    def __unicode__(self):
        return self.title
