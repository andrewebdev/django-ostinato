from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.conf import settings

from tagging.fields import TagField
from ostinato.managers import ContentItemManager
from ostinato.statemachine import StateMachine


OSTINATO_HOMEPAGE_SLUG = getattr(settings, 'OSTINATO_HOMEPAGE_SLUG', 'homepage')
OSTINATO_PAGE_TEMPLATES = getattr(settings, 'OSTINATO_PAGE_TEMPLATES', ({
    'name': 'basic_page',
    'templates': ['ostinato/basic_page.html', 'ostinato/basic_page_edit.html'],
    'contenttypes': ['ostinato.basicpage'],
},))
TEMPLATE_CHOICES = [(i['name'], i['name'].replace('_', ' ').capitalize()) \
                    for i in OSTINATO_PAGE_TEMPLATES]


class ContentItem(models.Model, StateMachine):
    """
    This is the main Content Item Class to which will point to the
    location where the content item is located. It will also function
    as a 'meta' model that contains various fields required by any
    standard CMS.
    """
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True,
        help_text="A url friendly slug. This field must be '%s', if this "\
                  "field is to be your home page." % OSTINATO_HOMEPAGE_SLUG)
    short_title = models.CharField(max_length=15, null=True, blank=True,
        help_text="A shorter title which can be used in menus etc. If this \
                   is not supplied then the normal title field will be used.")
    description = models.TextField(null=True, blank=True)

    template = models.CharField(max_length=50, choices=TEMPLATE_CHOICES)

    tags = TagField()

    location = models.CharField(max_length=200, blank=True, null=True,
        help_text="Use this to point to pages that does not belong to the CMS"\
                  " directly.")

    allow_comments = models.BooleanField(default=False)
    show_in_nav = models.BooleanField(default=False)
    show_in_sitemap = models.BooleanField(default=False)
    order = models.IntegerField(null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(null=True, blank=True)

    authors = models.ManyToManyField(User, null=True, blank=True,
        related_name="contentitems_authored")
    contributors = models.ManyToManyField(User, null=True, blank=True,
        related_name="contentitems_contributed")
    parent = models.ForeignKey('self', null=True, blank=True)

    # Required field for the statemachine
    _sm_state = models.CharField(max_length=100, default='Private')

    # Our ContentItem relations, these may be omitted, in which case only
    # the location field will be used.
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # Custom Managers
    objects = ContentItemManager()

    class Meta:
        ordering = ['order', 'id', 'title']

    def __unicode__(self):
        return "%s" % self.title

    def _get_parents(self):
        if self.parent:
            yield self.parent
            self.parent._get_parents()

    @models.permalink
    def perma_url(self, perma_data):
        return perma_data

    def get_absolute_url(self):
        # Cycle through the parents and generate the path
        if self.location:
            return self.location
        path = []
        for step in self._get_parents():
            if step.slug != OSTINATO_HOMEPAGE_SLUG:
                path.append(step.slug)
        if self.slug != OSTINATO_HOMEPAGE_SLUG:
            path.append(self.slug)
        return self.perma_url(('ostinato_contentitem_detail', None,
            {'path': '/'.join(path)}))

    @models.permalink
    def get_object_url(self):
        """ Returns the url for the related object """
        return self.content_object.get_absolute_url()

    @models.permalink
    def get_edit_url(self):
        return ('ostinato_contentitem_edit', None, {'slug': self.slug})

    def get_short_title(self):
        if self.short_title: return self.short_title
        else: return self.title

    ## Statemachine Actions
    def sm_post_action(self, **kwargs):
        """ Override so that we can set the publish date """
        if kwargs['action'] == 'Publish':
            self.publish_date = datetime.now()

        elif kwargs['action'] == 'Archive':
            self.allow_comments = False

        super(ContentItem, self).sm_post_action(**kwargs)

    def save(self, *args, **kwargs):
        # Generate a slug if we dont have one
        if not self.slug:
            self.slug = slugify(self.title)
        super(ContentItem, self).save(*args, **kwargs)


class BasicPage(models.Model):
    """
    A basic page for the user to create some content. Any instance of the
    ostinato page model will have a generic relation created in contentitem
    automatically on save, so it integrates tightly into this.
    """
    title = models.CharField(max_length=150)
    content = models.TextField()

    def __unicode__(self):
        return self.title