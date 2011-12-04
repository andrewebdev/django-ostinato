from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext as _
from django.template.defaultfilters import slugify
from django.conf import settings

from tagging.fields import TagField
from mptt.models import MPTTModel, TreeForeignKey

from ostinato.managers import ContentItemManager
from ostinato.statemachine.models import StateMachineBase, StateMachineField
from ostinato.statemachine.models import sm_post_action


OSTINATO_HOMEPAGE_SLUG = getattr(settings, 'OSTINATO_HOMEPAGE_SLUG', 'homepage')
OSTINATO_PAGE_TEMPLATES = getattr(settings, 'OSTINATO_PAGE_TEMPLATES', ({
    'name': 'basic_page',
    'templates': ['ostinato/basic_page.html', 'ostinato/basic_page_edit.html'],
    'contenttypes': ['ostinato.basicpage'],
},))
TEMPLATE_CHOICES = [(i['name'], i['name'].replace('_', ' ').capitalize()) \
                    for i in OSTINATO_PAGE_TEMPLATES]


class CMSStateMachine(StateMachineBase):

    class Meta:
        permissions = (
            ('make_public', 'Make Public'),
            ('make_private', 'Make Private'),
            ('archive', 'Archive')
        )
    
    class SMOptions:
        initial_state = 'private'
        state_actions = {
            'private': ('make_public',),
            'public': ('make_private', 'archive'),
            'archived': ('make_private',),
        }
        action_targets = {
            'make_public': 'public',
            'make_private': 'private',
            'archive': 'archived',
        }


class ContentItem(MPTTModel):
    """
    This is the main Content Item Class to which will point to the
    location where the content item is located. It will also function
    as a 'meta' model that contains various fields required by any
    standard CMS.
    """
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True,
        help_text='A url friendly slug. This field must be "%s", if this '\
                  'field is to be your home page.' % OSTINATO_HOMEPAGE_SLUG)
    short_title = models.CharField(max_length=15, null=True, blank=True,
        help_text='A shorter title which can be used in menus etc. If this \
                   is not supplied then the normal title field will be used.')
    description = models.TextField(null=True, blank=True)

    template = models.CharField(max_length=50, choices=TEMPLATE_CHOICES)

    tags = TagField()

    location = models.CharField(max_length=200, blank=True, null=True,
        help_text='Use this to point to pages that does not belong to the CMS'\
                  ' directly.')

    allow_comments = models.BooleanField(default=False)
    show_in_nav = models.BooleanField(default=False)
    show_in_sitemap = models.BooleanField(default=False)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(null=True, blank=True)

    authors = models.ManyToManyField(User, null=True, blank=True,
        related_name='contentitems_authored')
    contributors = models.ManyToManyField(User, null=True, blank=True,
        related_name='contentitems_contributed')

    parent = TreeForeignKey('self', null=True, blank=True,
        related_name='children')

    # Our ContentItem relations, these may be omitted, in which case only
    # the location field will be used.
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    # Custom Managers and Virtual Fields
    objects = ContentItemManager()
    sm = StateMachineField(CMSStateMachine)

    class Meta:
        ordering = ['id', 'title']

    def __unicode__(self):
        return "%s" % self.title

    def state(self):
        """ Just a helper for the admin """
        return self.sm.state

    ## TODO: This operation may be expensive? Cache this in some way?
    def _get_parents(self):
        if self.parent:
            for p in self.parent._get_parents():
                yield p
            yield self.parent

    @models.permalink
    def perma_url(self, perma_data):
        return perma_data

    def get_absolute_url(self):
        # Cycle through the parents and generate the path
        if self.location:
            return self.location
        if self.slug == OSTINATO_HOMEPAGE_SLUG:
            return '/'
        path = []
        for parent in self._get_parents():
            if parent.slug != OSTINATO_HOMEPAGE_SLUG:
                path.append(parent.slug)
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

    def save(self, *args, **kwargs):
        # Generate a slug if we dont have one
        if not self.slug:
            self.slug = slugify(self.title)
        super(ContentItem, self).save(*args, **kwargs)


# Other helper and demo classes
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

