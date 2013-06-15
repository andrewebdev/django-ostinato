from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.cache import get_cache
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from mptt.models import MPTTModel, TreeForeignKey

from ostinato.pages.managers import PageManager
from ostinato.pages.workflow import get_workflow


DEFAULT_STATE = getattr(settings, 'OSTINATO_PAGES_DEFAULT_STATE', 5)


class ContentError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


## Models
class Page(MPTTModel):
    """ A basic page model """
    slug = models.SlugField(
        _("Slug"), unique=True, help_text=_("A url friendly slug."))

    template = models.CharField(_("Template"), max_length=250)

    redirect = models.CharField(
        _("Redirect"), max_length=200, blank=True, null=True,
        help_text=_("Use this to point to redirect to another page or "
                    "website."))

    show_in_nav = models.BooleanField(_("Show in nav"), default=True)
    show_in_sitemap = models.BooleanField(_("Show in sitemap"), default=True)

    state = models.IntegerField(
        _("State"), default=DEFAULT_STATE, choices=get_workflow().get_choices())

    created_date = models.DateTimeField(_("Created date"), null=True, blank=True)
    modified_date = models.DateTimeField(_("Modified date"), null=True, blank=True)
    publish_date = models.DateTimeField(_("Published date"), null=True, blank=True)

    author = models.ForeignKey(
        User, verbose_name=_("Author"),
        related_name='pages_authored', null=True, blank=True)

    parent = TreeForeignKey(
        'self', verbose_name=_("Parent"),
        null=True, blank=True, related_name='page_children')

    objects = PageManager()

    class Meta:
        permissions = get_workflow().get_permissions()
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")

    def __unicode__(self):
        return self.slug

    def get_short_title(self):
        return self.slug

    def save(self, *args, **kwargs):
        now = timezone.now()

        if not self.id or not self.created_date:
            self.created_date = now

            # since it's created the first time, and we want it
            # published by default, we need to set the date now.
            if self.state == 5:
                self.publish_date = now

        self.modified_date = now

        page = super(Page, self).save(*args, **kwargs)

        # Make sure to clear the url, navbar and breadcrumbs cache
        Page.objects.clear_url_cache()
        Page.objects.clear_navbar_cache()
        Page.objects.clear_breadcrumbs_cache()
        return page

    @models.permalink
    def perma_url(self, data):
        """ A seperate method to specifically deal with permalinks """
        return data

    def get_absolute_url(self, clear_cache=False):
        """ Cycle through the parents and generate the path """
        cache = get_cache('default')
        cache_key = 'ostinato:pages:page:%s:url' % self.id

        if clear_cache:
            cache.delete(cache_key)

        url = cache.get(cache_key)

        if not url:
            if self.redirect:
                return self.redirect

            if self.is_root_node() and self == Page.objects.root_nodes()[0]:
                url = reverse('ostinato_page_home')

            else:
                path = list(self.get_ancestors().values_list('slug', flat=True))
                path.append(self.slug)
                url = self.perma_url(('ostinato_page_view', None, {
                    'path': '/'.join(path)
                }))

            # Set the cache to timeout after a month
            cache.set(cache_key, url, 60 * 60 * 24 * 7 * 4)

        # Now that we have the url, we should also cache the path lookup.
        # This is used by the PageManager.objects.get_from_path() to discover
        # a page based on the url path.
        url_cache_key = 'ostinato:pages:page_for_path:%s' % url
        cache.set(url_cache_key, self, 60 * 60 * 24 * 7 * 4)

        return url


class PageContent(models.Model):
    page = models.ForeignKey(Page)
    language = models.CharField(max_length=10, editable=False)
    created_date = models.DateTimeField(_("Created date"), auto_now_add=True)
    modified_date = models.DateTimeField(_("Modified date"), auto_now=True)

    class Meta:
        abstract = True


class MetaContent(PageContent):
    """
    This model serves as both an example, and as a default page content
    model that can be added to any templates. It contains some common fields
    that most CMS's require in some way.
    """
    title = models.CharField(max_length=250)
    short_title = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    meta_keywords = models.CharField(max_length=250, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
