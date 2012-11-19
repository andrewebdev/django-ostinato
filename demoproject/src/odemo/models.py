from django.db import models

from ostinato.pages.models import Page, PageContent
from ostinato.pages.registry import page_content
from ckeditor.fields import RichTextField


class Content(PageContent):
    """
    An example of how you would do mixins. A mixin must be an abstract
    model.
    """
    content = RichTextField()

    class Meta:
        abstract = True  # Required for mixins


class Contributor(models.Model):
    page = models.ForeignKey(Page)
    name = models.CharField(max_length=100)


# Actual Page Content
@page_content.register
class LandingPage(PageContent):
    intro = models.TextField()

    # We are overriding this, since we just want to change the order.
    # This could probably also be done by overriding the form.
    content = RichTextField()

    class ContentOptions:
        template = 'pages/tests/landing_page.html'
        admin_inlines = ['odemo.admin.ContributorInline']


@page_content.register
class BasicPage(Content):

    class ContentOptions:
        template = 'pages/tests/basic_page.html'
        view = 'ostinato.pages.views.CustomView'


@page_content.register
class ContactPage(Content):

    class ContentOptions:
        template = 'page_templates/contact_page.html'
        view = 'odemo.views.ContactView'


@page_content.register
class ListPage(Content):
    """ Example of a page that uses a custom form """

    related_page_group = models.ForeignKey(Page,
        related_name='related_to_listpage')

    class ContentOptions:
        template = 'page_templates/list_page.html'
        form = 'odemo.forms.CustomForm'


