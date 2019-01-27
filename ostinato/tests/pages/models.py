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
class ContentBase(PageContent):
    """
    An example of how you would do mixins. A mixin must be an abstract
    model.
    """
    content = models.TextField()

    class Meta:
        abstract = True  # Required for mixins


class LandingPage(ContentBase):
    intro = models.TextField()


class BasicPage(ContentBase):
    pass


class BasicPageFunc(ContentBase):
    """
    A page that makes use of the old school function based views.
    """
    pass


class OtherPage(ContentBase):
    """ Test content that doesn't have a template specified """
    class Meta:
        verbose_name = 'Some Other Page'

