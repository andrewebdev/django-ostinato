from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.conf import settings

from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

from ostinato.pages.managers import PageManager
from ostinato.statemachine.models import StateMachineField, DefaultStateMachine


TEMPLATE_CHOICES = getattr(settings, 'OSTINATO_PAGE_TEMPLATES')


## Models
class Page(MPTTModel):
    """ A basic page model """
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, help_text='A url friendly slug.')
    short_title = models.CharField(max_length=15, null=True, blank=True,
        help_text='A shorter title which can be used in menus etc. If this \
                   is not supplied then the normal title field will be used.')

    template = models.CharField(max_length=100, choices=TEMPLATE_CHOICES)

    redirect = models.CharField(max_length=200, blank=True, null=True,
        help_text='Use this to point to redirect to another page or website.')

    show_in_nav = models.BooleanField(default=False)
    show_in_sitemap = models.BooleanField(default=False)

    created_date = models.DateTimeField(null=True, blank=True)
    modified_date = models.DateTimeField(null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)

    author = models.ForeignKey(User, related_name='pages_authored',
        null=True, blank=True)

    parent = TreeForeignKey('self', null=True, blank=True,
        related_name='page_children') 

    ## Managers
    objects = PageManager()
    tree = TreeManager()

    sm = StateMachineField(DefaultStateMachine)
    ## GenericRelation gives us extra api methods
    _sm = generic.GenericRelation(DefaultStateMachine)

    ## required for caching contents
    _contents = None

    def __unicode__(self):
        return '%s' % self.title


    def save(self, *args, **kwargs):
        ## Publishing
        if not self.id or not self.created_date:
            self.created_date = timezone.now()
        self.modified_date = timezone.now()
        super(Page, self).save(*args, **kwargs)


    def get_short_title(self):
        if self.short_title:
            return self.short_title
        else:
            return self.title


    @models.permalink
    def perma_url(self, data):
        """ A seperate method to specifically deal with permalinks """
        return data


    def get_absolute_url(self):
        """ Cycle through the parents and generate the path """

        if self.redirect:
            return self.redirect

        if self == Page.tree.root_nodes()[0]:
            return reverse('ostinato_page_home')

        path = []
        for parent in self.get_ancestors():
            path.append(parent.slug)

        path.append(self.slug)

        return self.perma_url(
            ('ostinato_page_view', None, {'path': '/'.join(path)}) )


    def get_content_model(self):
        label, model = self.template.split('.')
        content_type = ContentType.objects.get(app_label=label, model=model)
        return content_type.model_class()


    def get_content(self):
        if not self._contents:
            label, model = self.template.split('.')
            content_type = ContentType.objects.get(app_label=label, model=model)
            self._contents = content_type.get_object_for_this_type(page=self.id)

        return self._contents

    contents = property(get_content)


    def get_template(self):
        return self.get_content_model().ContentOptions.template


@receiver(pre_save, sender=Page)
def update_publish_date(sender, **kwargs):
    if kwargs['instance'].sm:
        if not kwargs['instance'].publish_date and \
                kwargs['instance'].sm.state == 'published':
            kwargs['instance'].publish_date = timezone.now()


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
        ``view`` is a custom view that will handle the rendering for the page
        """
        template = None
        view = 'ostinato.pages.views.PageView'

    @classmethod
    def get_template(cls):
        return cls.ContentOptions.template


## Example Templates
class ContentMixin(models.Model):
    """
    An example of how you would do mixins. A mixin must be an abstract
    model.
    """
    content = models.TextField()

    class Meta:
        abstract = True  # Required for mixins


class LandingPage(ContentMixin, PageContent):
    intro = models.TextField()

    class ContentOptions:
        template = 'pages/tests/landing_page.html'


class BasicPage(ContentMixin, PageContent):

    class ContentOptions:
        template = 'pages/tests/basic_page.html'
        view = 'ostinato.pages.views.CustomView'

