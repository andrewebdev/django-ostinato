from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from ostinato.signals import *
from ostinato.managers import ContentItemManager

# Snippet of code borrowed from django-photologue
# attempt to load the django-tagging TagField from default location,
# otherwise we substitude a dummy TagField.
try:
    from tagging.fields import TagField
    tagfield_help_text = 'Separate tags with spaces, put quotes around multiple-word tags.'
except ImportError:
    class TagField(models.CharField):
        def __init__(self, **kwargs):
            default_kwargs = {'max_length': 255, 'blank': True}
            default_kwargs.update(kwargs)
            super(TagField, self).__init__(**default_kwargs)
        def get_internal_type(self):
            return 'CharField'
    tagfield_help_text = 'Django-tagging was not found, tags will be treated as plain text.'
## End snippet

class ContentItem(models.Model):
    """
    This is the main Content Item Class to which will point to the
    location where the content item is located. It will also function
    as a 'meta' model that contains various fields required by any
    standard CMS.

    """
    DRAFT = 0
    REVIEW = 1
    PUBLISHED = 2
    HIDDEN = 3
    STATE = (
        (DRAFT, 'Draft'),
        (REVIEW, 'To Review'),
        (PUBLISHED, 'Published'),
        (HIDDEN, 'Hidden'),
    )

    title = models.CharField(max_length=150)
    short_title = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        help_text="A shorter title which can be used in menus etc. If this is not supplied then the normal title field will be used.",
    )
    description = models.TextField(null=True, blank=True)
    tags = TagField()
    status = models.IntegerField(choices=STATE, default=DRAFT)
    allow_comments = models.BooleanField(default=True)
    show_in_nav = models.BooleanField(default=True)
    location = models.URLField(
        null=True,
        blank=True,
        verify_exists=False,
        help_text="The location of the item on the site, ie: /article/hello-world/",
    )
    # show_in_sitemap may confuse developers into thinking it refers to the
    # standard django sitemaps framework. So till we decide what to do with
    # this I'll just keep it commented out for now.
    #
    # show_in_sitemap = models.BooleanField(default=True)
    #
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

    def __unicode__(self):
        return "%s" % self.title

    def get_absolute_url(self):
        """
        First we check if we are pointint to another content_type directly.
        If so, check if that item has a ``get_absolute_url`` method, and use
        it's own method.

        If the target content_item does not have a ``get_absolute_url`` method
        definde, then we use the ``location`` field to determine the url.

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

    def action_publish(self):
        """ A method to publish the current content_item """
        if not self.publish_date:
            self.publish_date = datetime.now()
        self.status = self.PUBLISHED
        self.save()
        post_action_publish.send(sender=self)

    def action_review(self):
        """ A method to mark the item for review """
        self.status = self.REVIEW
        self.save()
        post_action_review.send(sender=self)

    def action_hide(self):
        """ A method to hide the content item """
        self.status = self.HIDDEN
        self.save()
        post_action_hide.send(sender=self)

    def action_draft(self):
        """ A method to set the item in the Draft state """
        self.status = self.DRAFT
        self.save()
        post_action_draft.send(sender=self)
