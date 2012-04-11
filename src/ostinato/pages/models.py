from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils import timezone

from mptt.models import MPTTModel, TreeForeignKey

from ostinato.pages.pages_registry import PageTemplate, page_templates


## Some Utility
def get_template_choices():
    choices = ()
    for template in page_templates.all():
        choices += ((template.template_id, template.description),)
    return choices


def get_zones(page):
    zones = []
    page_template = PageTemplate.get_template_by_id(page.template)

    for index, zone in enumerate(page_template.zones):
        zone_id = zone[0]
        app_label = zone[1].split('.')[0]
        model = zone[1].split('.')[1]

        ct = ContentType.objects.get(app_label=app_label, model=model)
        instance, created = ct.model_class().objects.get_or_create(
            page=page, zone_id=zone_id)

        zones.append(instance)

    return zones


## Managers
class PageManager(models.Manager):

    def get_zones_for_page(self, slug=None, page=None):
        if not page:
            page = self.get_query_set().get(slug=slug)

        return get_zones(page)


## Models
class Page(MPTTModel):
    """ A basic page model """
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, help_text='A url friendly slug.')
    short_title = models.CharField(max_length=15, null=True, blank=True,
        help_text='A shorter title which can be used in menus etc. If this \
                   is not supplied then the normal title field will be used.')

    template = models.CharField(max_length='50', choices=get_template_choices())

    location = models.CharField(max_length=200, blank=True, null=True,
        help_text='Use this to point to pages that does not belong to the CMS'\
                  ' directly.')

    show_in_nav = models.BooleanField(default=False)
    show_in_sitemap = models.BooleanField(default=False)

    created_date = models.DateTimeField()
    modified_date = models.DateTimeField()
    publish_date = models.DateTimeField(null=True, blank=True)

    author = models.ForeignKey(User, related_name='pages_authored')

    parent = TreeForeignKey('self', null=True, blank=True,
        related_name='page_children') 

    objects = PageManager()

    def save(self, *args, **kwargs):
        if not self.id or not self.created_date:
            self.created_date = timezone.now()
        self.modified_date = timezone.now()
        super(Page, self).save(*args, **kwargs)

    def get_zones(self):
        """ Retrieve all the zones for this page, base on it's template """
        if not self.id:
            return None

        return get_zones(self)

    @models.permalink
    def perma_url(self, data):
        """ A seperate method to specifically deal with permalinks """
        return data

    def get_absolute_url(self):
        """ Cycle through the parents and generate the path """

        if self.location:
            return self.location

        if self.lft == 1:
            return reverse('ostinato_page_home')

        path = []
        for parent in self.get_ancestors():
            path.append(parent.slug)

        path.append(self.slug)

        return self.perma_url(
            ('ostinato_page_view', None, {'path': '/'.join(path)}) )


class ZoneContent(models.Model):
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


class PageMeta(ZoneContent):
    """
    This contains some extra meta fields for our page.
    This model also serves as an example of how to create your own zones.
    """
    description = models.TextField(null=True, blank=True)    
    allow_comments = models.BooleanField(default=False)
    contributors = models.ManyToManyField(User, null=True, blank=True,
        related_name='pages_contributed')


class BasicTextZone(ZoneContent):
    """ A standard text field """
    content = models.TextField(null=True, blank=True)

