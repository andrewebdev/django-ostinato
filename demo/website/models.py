from django.db import models

from mptt.fields import TreeForeignKey
from ostinato.pages.models import Page, PageContent
from ostinato.pages.registry import page_content

from ostinato.medialib.models import MediaItem


# Page Media
class Image(MediaItem):
    image = models.ImageField(upload_to="uploads/")

    def __unicode__(self):
        return "Image - %s" % self.title


class Video(MediaItem):
    video_url = models.URLField()

    def __unicode__(self):
        return "Video - %s" % self.title


# Page content mixin that allows easy access to page media
class PageMediaMixin(object):

    def get_media(self, model):
        return model.objects.filter(content_type__app_label='ostinato_pages',
                                    content_type__model='page',
                                    object_id=self.page.id)

    @property
    def images(self):
        return self.get_media(Image).filter(is_visible=True)

    @property
    def videos(self):
        return self.get_media(Video).filter(is_visible=True)


# Page Templates
class SEOPage(PageContent):
    meta_keywords = models.CharField(max_length=250, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True

    def get_keywords(self):
        """
        Returns the meta_keywords but if the field is empty,
        traverse up the tree to the first ancestor that have keywords,
        and return that value.
        """
        # TODO
        # Also remember to cache the result so that we dont have to do
        # the expensive traversal every time.
        return self.meta_keywords

    def get_description(self):
        """
        Returns the meta_description, but if the field is empty,
        traverse up the tree to the first ancestor that have a description,
        and return that value.
        """
        # TODO
        # Also remember to cache the result so that we dont have to do
        # the expensive traversal every time.
        return self.meta_description


@page_content.register
class HomePage(PageMediaMixin, SEOPage):
    content = models.TextField()

    class ContentOptions:
        form = 'website.forms.HomePageForm'
        view = 'website.views.HomePageView'
        admin_inlines = ['website.forms.ImageInline',
                         'website.forms.VideoInline']


@page_content.register
class GenericPage(SEOPage):
    content = models.TextField()

    class ContentOptions:
        form = 'website.forms.GenericPageForm'
        view = 'website.views.GenericPageView'


@page_content.register
class TopLevelListPage(SEOPage):
    class ContentOptions:
        view = 'website.views.TopLevelListPageView'


@page_content.register
class CaseStudyPage(SEOPage):
    content = models.TextField()

    class ContentOptions:
        form = 'website.forms.GenericPageForm'
        view = 'website.views.CaseStudyPageView'


@page_content.register
class ContactPage(SEOPage):
    content = models.TextField()

    recipients = models.TextField(
        help_text="A comma separated list of recipient emails")
    email_subject = models.CharField(max_length=250)
    success_page = TreeForeignKey(
        Page, help_text="The page to show the user once the form was "
                        "succesfully submitted")

    class ContentOptions:
        form = 'website.forms.ContactPageForm'
        view = 'website.views.ContactPageView'

    def get_next_url(self):
        return self.success_page.get_absolute_url()

    def get_recipients(self):
        return [i for i in self.recipients.replace(' ', '').split(',')]
