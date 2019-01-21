from django.db import models
from django.contrib import admin

from ostinato.pages.models import Page, PageContent


# Create some extra models to be used by some page content
class Photo(models.Model):
    photo_path = models.CharField(max_length=250)


class Contributor(models.Model):
    page = models.ForeignKey(
        Page,
        related_name='testing',
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=50)

    # Required to test the inlines with through model
    photos = models.ManyToManyField(
        Photo,
        through='ContributorPhotos',
        blank=True,
    )


class ContributorPhotos(models.Model):
    contributor = models.ForeignKey(Contributor, on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    order = models.IntegerField(default=1)


class ContributorInline(admin.StackedInline):
    model = Contributor


class PhotoInline(admin.StackedInline):
    model = Contributor.photos.through


# Create and register the Page Content models
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
        template = 'pages/landing_page.html'


class BasicPage(ContentMixin, PageContent):

    class ContentOptions:
        template = 'pages/basic_page.html'
        view = 'ostinato.tests.pages.views.CustomView'
        admin_inlines = [
            'ostinato.tests.pages.models.ContributorInline',
        ]


class BasicPageFunc(ContentMixin, PageContent):
    """
    A page that makes use of the old school function based views.
    """
    class ContentOptions:
        template = 'pages/basic_page.html'
        view = 'ostinato.tests.pages.views.functionview'


class OtherPage(ContentMixin, PageContent):
    """ Test content that doesn't have a template specified """

    class Meta:
        verbose_name = 'Some Other Page'

