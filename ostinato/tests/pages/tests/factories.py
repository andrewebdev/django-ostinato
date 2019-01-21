import factory
from factory.django import DjangoModelFactory

from django.utils import timezone

from ostinato.pages.models import Page
from ostinato.tests.pages.models import (
    LandingPage,
    BasicPage,
    BasicPageFunc,
    OtherPage,
)

now = timezone.now()


# Core Ostinato Page Model
class PageFactory(DjangoModelFactory):

    title = factory.Sequence(lambda n: "Page {0} Title".format(n))
    slug = factory.Sequence(lambda n: "page-{0}-slug".format(n))
    created_date = now
    modified_date = now
    template = "ostinato_pages.basicpage"

    class Meta:
        model = Page


# Custom PageContent models for the tests
class LandingPageFactory(DjangoModelFactory):
    page = factory.SubFactory(PageFactory)
    intro = "Landing Page Intro"
    content = "Some content for the page"

    class Meta:
        model = LandingPage


class BasicPageFactory(DjangoModelFactory):
    page = factory.SubFactory(PageFactory)
    content = "Some content for the page"

    class Meta:
        model = BasicPage


class BasicPageFuncFactory(DjangoModelFactory):
    page = factory.SubFactory(PageFactory)
    content = "Some content for the page"

    class Meta:
        model = BasicPageFunc


class OtherPageFactory(DjangoModelFactory):
    page = factory.SubFactory(PageFactory)
    content = "Some content for the page"

    class Meta:
        model = OtherPage

