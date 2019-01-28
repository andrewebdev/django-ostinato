from django.db import models
from django.urls import reverse
from django.core.cache import caches
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from mptt.models import MPTTModel, TreeForeignKey

from ostinato.pages.managers import PageManager
from ostinato.pages.workflow import get_workflow
from ostinato.pages import PAGES_SETTINGS, get_cache_key


class ContentError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


def _clear_cache():
    Page.objects.clear_url_cache()
    Page.objects.clear_breadcrumbs_cache()


def get_content_model(app_model):
    app, model = app_model.split('.')
    ct = ContentType.objects.get(
        app_label=app,
        model=model
    )
    return ct.model_class()


def get_template_options(template_id):
    return PAGES_SETTINGS['templates'].get(template_id)


# Models
class Page(MPTTModel):
    """ A basic page model """
    title = models.CharField(_("Title"), max_length=150)

    slug = models.SlugField(
        _("Slug"),
        unique=True,
        help_text=_("A url friendly slug."),
    )

    short_title = models.CharField(
        _("Short title"),
        max_length=50,
        null=True,
        blank=True,
        help_text=_(
            "A shorter title which can be used in menus etc. If this is not "
            "supplied then the normal title field will be used."
        ),
    )

    template = models.CharField(_("Template"), max_length=250)

    redirect = models.CharField(
        _("Redirect"),
        max_length=200,
        blank=True,
        null=True,
        help_text=_(
            "Use this to point to redirect to another page or website."
        ),
    )

    show_in_sitemap = models.BooleanField(_("Show in sitemap"), default=True)

    state = models.CharField(
        _("State"),
        max_length=20,
        default=PAGES_SETTINGS['default_state'],
        choices=get_workflow().get_choices(),
    )

    created_date = models.DateTimeField(
        _("Created date"),
        null=True,
        blank=True,
    )

    modified_date = models.DateTimeField(
        _("Modified date"),
        null=True,
        blank=True,
    )

    publish_date = models.DateTimeField(
        _("Published date"),
        null=True,
        blank=True,
    )

    parent = TreeForeignKey(
        'self',
        verbose_name=_("Parent"),
        null=True,
        blank=True,
        related_name='page_children',
        on_delete=models.SET_NULL,
    )

    # Managers
    objects = PageManager()

    class Meta:
        permissions = get_workflow().get_permissions('page', 'Page')
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")

    def __str__(self):
        return '%s' % self.title

    def save(self, *args, **kwargs):
        now = timezone.now()

        if not self.id or not self.created_date:
            self.created_date = now

            # since it's created the first time, and we want it
            # published by default, we need to set the date now.
            if self.state == 'public':
                self.publish_date = now

        self.modified_date = now

        page = super(Page, self).save(*args, **kwargs)

        # Make sure to clear the url and breadcrumbs cache
        _clear_cache()
        return page

    def delete(self, *args, **kwargs):
        """
        When a page is deleted we need to remove it's items from the
        url and breadcrumb cache.
        """
        _clear_cache()
        super(Page, self).delete(*args, **kwargs)

    def get_short_title(self):
        if self.short_title:
            return self.short_title
        else:
            return self.title

    def get_absolute_url(self, clear_cache=False):
        """ Cycle through the parents and generate the path """
        cache = caches[PAGES_SETTINGS['cache_name']]
        cache_key = get_cache_key('page', str(self.id), 'url')

        if clear_cache:
            cache.delete(cache_key)

        url = cache.get(cache_key)

        if not url:
            if self.redirect:
                return self.redirect

            if self.is_root_node() and self == Page.objects.root_nodes()[0]:
                url = reverse('ostinato_page_home')

            else:
                path = list(self.get_ancestors().values_list('slug',
                                                             flat=True))
                path.append(self.slug)
                url = reverse('ostinato_page_view', kwargs={
                    'path': '/'.join(path)
                })

            # Set the cache to timeout after a month
            cache.set(cache_key, url, 60 * 60 * 24 * 7 * 4)

        # Now that we have the url, we should also cache the path lookup.
        # This is used by the PageManager.objects.get_from_path() to discover
        # a page based on the url path.
        url_cache_key = get_cache_key('page_for_path', url)
        cache.set(url_cache_key, self, 60 * 60 * 24 * 7 * 4)

        return url

    @cached_property
    def contents(self):
        """
        Returns the content for this page or None if it doesn't exist.
        """
        obj_model = get_content_model(self.template)
        try:
            return obj_model.objects.get(page=self.id)
        except obj_model.DoesNotExist:
            return None

    def get_template(self):
        template_opts = get_template_options(self.template)
        template = template_opts.get('template', None)

        if not template:
            template_name = self.template.replace('.', '_')
            template = 'pages/{0}.html'.format(template_name)

        return template


class PageContent(models.Model):
    """
    Our base PageContent model. All other content models need to subclass
    this one.
    """
    page = models.OneToOneField(
        Page,
        related_name='%(app_label)s_%(class)s_content',
        on_delete=models.CASCADE)

    class Meta:
        abstract = True
