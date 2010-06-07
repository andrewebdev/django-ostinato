from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

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
    authors = models.ManyToManyField(User, null=True, blank=True)
    contributors = models.ManyToManyField(User, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)

    # Our ContentItem relations, these may be omitted, in which case only
    # the location field will be used.
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

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
        return self.location

    def action_publish(self):
        """ A method to publish the current content_item """
        pass

    def action_review(self):
        """ A method to mark the item for review """
        pass

    def action_hide(self):
        """ A method to hide the content item """
        pass

    def action_draft(self):
        """ A method to set the item in the Draft state """
        pass
