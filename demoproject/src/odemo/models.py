from django.db import models
from ostinato.pages.models import PageContent, ContentMixin, Page

from ckeditor.fields import RichTextField


class CKContentMixin(PageContent):
    """ An Example of using a custom field directly on the model """

    content = RichTextField()

    class Meta:
        abstract = True


class ContactPage(CKContentMixin):

    class ContentOptions:
        template = 'page_templates/contact_page.html'
        view = 'odemo.views.ContactView'


class ListPage(ContentMixin, PageContent):
    """ Example of a page that uses a custom form """

    related_page_group = models.ForeignKey(Page,
        related_name='related_to_listpage')

    class ContentOptions:
        template = 'page_templates/list_page.html'
        form = 'odemo.forms.CustomForm'

