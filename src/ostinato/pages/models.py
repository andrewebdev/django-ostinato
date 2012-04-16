from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import pre_save

from mptt.models import MPTTModel, TreeForeignKey

from ostinato.pages.utils import get_zones_for, get_page_zone_by_id
from ostinato.statemachine.models import StateMachineField, DefaultStateMachine


PAGE_TEMPLATES = getattr(settings, 'OSTINATO_PAGE_TEMPLATES')
TEMPLATE_CHOICES = [(t['name'], t['description']) for t in PAGE_TEMPLATES]


## Managers
class PageManager(models.Manager):

    def get_zones_for_page(self, slug=None, page=None):
        if not page:
            page = self.get_query_set().get(slug=slug)

        return get_zones_for(page)

    def published(self):
        now = timezone.now()
        return self.get_query_set().filter(
            publish_date__lte=now, _sm__state='published').distinct()

    def get_navbar(self, for_page=None):
        """
        Returns a dictionary of pages with their short titles and urls.

        ``for_page`` is an instance of Page. If specified, will only
        return immediate child pages for that page.
        """
        to_return = []
        nav_items = self.published().filter(parent=for_page, show_in_nav=True)

        if nav_items:
            for item in nav_items:
                to_return.append({
                    'title': item.get_short_title(),
                    'url': item.get_absolute_url(),
                })

        return to_return


## Models
class Page(MPTTModel):
    """ A basic page model """
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, help_text='A url friendly slug.')
    short_title = models.CharField(max_length=15, null=True, blank=True,
        help_text='A shorter title which can be used in menus etc. If this \
                   is not supplied then the normal title field will be used.')

    template = models.CharField(max_length='50', choices=TEMPLATE_CHOICES,
        default=TEMPLATE_CHOICES[0][0])

    redirect = models.CharField(max_length=200, blank=True, null=True,
        help_text='Use this to point to redirect to another page or website.')

    show_in_nav = models.BooleanField(default=False)
    show_in_sitemap = models.BooleanField(default=False)

    created_date = models.DateTimeField(null=True, blank=True)
    modified_date = models.DateTimeField(null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)

    author = models.ForeignKey(User, related_name='pages_authored')

    parent = TreeForeignKey('self', null=True, blank=True,
        related_name='page_children') 

    objects = PageManager()
    sm = StateMachineField(DefaultStateMachine)
    ## GenericRelation gives us extra api methods
    _sm = generic.GenericRelation(DefaultStateMachine)

    def __unicode__(self):
        return '%s' % self.title

    def save(self, *args, **kwargs):
        if not self.id or not self.created_date:
            self.created_date = timezone.now()
        self.modified_date = timezone.now()
        super(Page, self).save(*args, **kwargs)

    def state(self):
        """ Just a helper for the admin """
        return self.sm.state
        
    def get_short_title(self):
        if self.short_title:
            return self.short_title
        else:
            return self.title

    def get_zones(self):
        """ Retrieve all the zones for this page, base on it's template """
        if not self.id:
            return None

        return get_zones_for(self)

    def get_zone_by_id(self, zone_id):
        return get_page_zone_by_id(self, zone_id)

    @models.permalink
    def perma_url(self, data):
        """ A seperate method to specifically deal with permalinks """
        return data

    def get_absolute_url(self):
        """ Cycle through the parents and generate the path """

        if self.redirect:
            return self.redirect

        if self.lft == 1:
            return reverse('ostinato_page_home')

        path = []
        for parent in self.get_ancestors():
            path.append(parent.slug)

        path.append(self.slug)

        return self.perma_url(
            ('ostinato_page_view', None, {'path': '/'.join(path)}) )


@receiver(pre_save, sender=Page)
def update_publish_date(sender, **kwargs):
    if not kwargs['instance'].publish_date and \
            kwargs['instance'].sm.state == 'published':
        kwargs['instance'].publish_date = timezone.now()


## Content Zones
class ContentZone(models.Model):
    """
    This is our most basic content item.
    We can create our own zones by subclassing this one, and allows us
    to have a lot more control over our zones.
    """
    page = models.ForeignKey(Page)
    zone_id = models.CharField(max_length=50)

    class Meta:
        abstract = True
        unique_together = ('page', 'zone_id')

    def __unicode__(self):
        return '%s for %s' % (self.zone_id, self.page)


class PageMeta(ContentZone):
    """
    This contains some extra meta fields for our page.
    This model also serves as an example of how to create your own zones.
    """
    description = models.TextField(null=True, blank=True)    
    allow_comments = models.BooleanField(default=False)
    contributors = models.ManyToManyField(User, null=True, blank=True,
        related_name='pages_contributed')


class BasicTextZone(ContentZone):
    """ A standard text field """
    content = models.TextField(null=True, blank=True)

