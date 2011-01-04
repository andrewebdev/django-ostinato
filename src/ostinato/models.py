from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _

from tagging.fields import TagField
from ostinato.managers import ContentItemManager
from ostinato.statemachine import StateMachine

class ContentItem(models.Model, StateMachine):
    """
    This is the main Content Item Class to which will point to the
    location where the content item is located. It will also function
    as a 'meta' model that contains various fields required by any
    standard CMS.
    """
    title = models.CharField(max_length=150)
    short_title = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        help_text="A shorter title which can be used in menus etc. If this is not supplied then the normal title field will be used.",
    )
    description = models.TextField(null=True, blank=True)

    tags = TagField()

    allow_comments = models.BooleanField(default=True)
    show_in_nav = models.BooleanField(default=True)
    show_in_sitemap = models.BooleanField(default=True)
    order = models.IntegerField(null=True, blank=True)

    location = models.CharField(
        null=True,
        blank=True,
        max_length=250,
        help_text="The location of the item on the site, ie: /article/hello-world/",
    )

    # Required field for the statemachine to work
    sm_state = models.CharField(max_length=100, null=True, blank=True,
                                editable=False)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(null=True, blank=True)

    authors = models.ManyToManyField(
        User,
        null=True,
        blank=True,
        related_name="contentitems_authored",
    )
    contributors = models.ManyToManyField(
        User,
        null=True,
        blank=True,
        related_name="contentitems_contributed",
    )
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
    )

    # Our ContentItem relations, these may be omitted, in which case only
    # the location field will be used.
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # Custom Managers
    objects = ContentItemManager()

    class Meta:
        ordering = ['order', 'title']

    def __unicode__(self):
        return "%s" % self.title

    def save(self, *args, **kwargs):
        # if not self.publish_date and self.status == self.PUBLISHED:
        #     self.action_publish()
        super(ContentItem, self).save(*args, **kwargs)

    def get_absolute_url(self):
        """
        First we check if we are pointing to another content_type
        directly. If so, check if that item has a ``get_absolute_url``
        method, and use it's own method.

        If the target content_item does not have a ``get_absolute_url``
        method definded, then we use the ``location`` field to determine
        the url.

        """
        try:
            return self.content_object.get_absolute_url()
        except AttributeError:
            if self.location:
                return "%s" % self.location
            else:
                return None

    def get_short_title(self):
        if self.short_title:
            return self.short_title
        else:
            return self.title
