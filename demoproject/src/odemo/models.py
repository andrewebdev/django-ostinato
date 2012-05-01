from ostinato.pages.models import PageContent, ContentMixin


class ContactPage(ContentMixin, PageContent):

    class ContentOptions:
        template = 'page_templates/contact_page.html'
        view = 'odemo.views.ContactView'


class ListPage(ContentMixin, PageContent):

    class ContentOptions:
        template = 'page_templates/list_page.html'

