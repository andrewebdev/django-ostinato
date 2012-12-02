import re

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.core.exceptions import FieldError
from django.core.cache import get_cache
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.conf import settings

from mptt.models import MPTTModel, TreeForeignKey

from ostinato.pages.managers import PageManager
from ostinato.pages.workflow import PageWorkflow


DEFAULT_STATE = getattr(settings, 'OSTINATO_PAGES_DEFAULT_STATE', 5)


## Models
class Page(MPTTModel):
    """ A basic page model """
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, help_text='A url friendly slug.')
    short_title = models.CharField(max_length=50, null=True, blank=True,
        help_text='A shorter title which can be used in menus etc. If this \
                   is not supplied then the normal title field will be used.')

    template = models.CharField(max_length=250) 

    redirect = models.CharField(max_length=200, blank=True, null=True,
        help_text='Use this to point to redirect to another page or website.')

    show_in_nav = models.BooleanField(default=True)
    show_in_sitemap = models.BooleanField(default=True)

    state = models.IntegerField(default=DEFAULT_STATE,
        choices=PageWorkflow.get_choices())

    created_date = models.DateTimeField(null=True, blank=True)
    modified_date = models.DateTimeField(null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)

    author = models.ForeignKey(User, related_name='pages_authored',
        null=True, blank=True)

    parent = TreeForeignKey('self', null=True, blank=True,
        related_name='page_children') 

    ## Managers
    objects = PageManager()

    ## Required for caching some objects
    _contents = None
    _content_model = None


    class Meta:
        permissions = PageWorkflow.get_permissions()


    def __unicode__(self):
        return '%s' % self.title


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

        # Now that the page is saved, we reset and cache the url
        Page.objects.clear_url_cache()

        return page


    def get_short_title(self):
        if self.short_title:
            return self.short_title
        else:
            return self.title


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

        # Try to get the path from the cache
        url = cache.get(cache_key)

        if not url:
            # Generate the url and add it to the cache
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

            # Set the cache
            cache.set(cache_key, url, 1 * 60 * 60)

        return url


    def get_content_model(self):
        if not self._content_model:
            label, model = self.template.split('.')
            content_type = ContentType.objects.get(app_label=label, model=model)
            self._content_model = content_type.model_class()
        return self._content_model


    def get_content(self):
        """
        Returns the content for this page or None if it doesn't exist.
        """
        if not self._contents:
            obj_model = self.get_content_model()
            try:
                self._contents = obj_model.objects.get(page=self.id)
            except obj_model.DoesNotExist:
                pass
        return self._contents

    contents = property(get_content)


    def get_template(self):
        return self.get_content_model().get_template()


## Page Templates
class PageContent(models.Model):
    """
    Our base PageContent model. All other content models need to subclass
    this one.
    """

    page = models.OneToOneField(Page,
        related_name='%(app_label)s_%(class)s_content')

    class Meta:
        abstract = True

    class ContentOptions:
        """
        Custom Options for the Content
        ``template`` is the template path relative the templatedirs.
        ``view`` is a custom view that will handle the rendering for the page.
        ``form`` a custom form to use in the admin.
        """
        template = None
        view = 'ostinato.pages.views.PageView'
        form = None
        admin_inlines = []


    def add_content(self, **kwargs):
        for k in kwargs:

            if hasattr(self, k):
                raise Exception('Cannot add "%s" to %s since that attribute'
                    'already exists.' % (k, self))

            self.__dict__[k] = kwargs[k]


    @classmethod
    def get_template(cls):
        template = getattr(cls.ContentOptions, 'template', None)

        if not template:
            cls_name = re.findall('[A-Z][^A-Z]*', cls.__name__)
            template = 'pages/%s.html' % '_'.join([i.lower() for i in cls_name])

        return template

