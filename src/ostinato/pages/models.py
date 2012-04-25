from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import pre_save

from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

from ostinato.pages.managers import PageManager
from ostinato.statemachine.models import StateMachineField, DefaultStateMachine


## Models
class Page(MPTTModel):
    """ A basic page model """
    title = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, help_text='A url friendly slug.')
    short_title = models.CharField(max_length=15, null=True, blank=True,
        help_text='A shorter title which can be used in menus etc. If this \
                   is not supplied then the normal title field will be used.')

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

    ## Create a Generic relation for the Page Template
    template = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content = generic.GenericForeignKey('template', 'object_id')

    ## Managers
    objects = PageManager()
    tree = TreeManager()

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


@receiver(pre_save, sender=Page)
def update_publish_date(sender, **kwargs):
    if kwargs['instance'].sm:
        if not kwargs['instance'].publish_date and \
                kwargs['instance'].sm.state == 'published':
            kwargs['instance'].publish_date = timezone.now()


## Page Templates
class PageTemplate(models.Model):
    """
    Page template does not know anything about instances of it.
    It only contains the template name, plus any fields that the 
    developer defines.

    """
    class Meta:
        abstract = True

    class TemplateMeta:
        """
        Custom Meta for the template.

        ``template`` is the template path relative the templatedirs.
        ``template_name`` is a verbose name for the template.

        """
        template = None

    @classmethod
    def get_template(cls):
        """ Returns a tuple containing ``template``, ``tempalte_name`` """
        return cls.TemplateMeta.template, cls._meta.verbose_name

