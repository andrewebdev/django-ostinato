from ostinato.pages.models import PageContent, ContentMixin

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

    class ContentOptions:
        template = 'page_templates/list_page.html'
        form = 'odemo.forms.CustomForm'

