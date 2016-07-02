from django import http

from ostinato.pages.views import PageView
from ostinato.pages.models import Page
from ostinato.contentbrowser.views import BrowserView

from website.forms import ContactForm
from blog.models import Entry


class TopLevelListPageView(PageView):

    def get_context_data(self, **kwargs):
        c = super(TopLevelListPageView, self).get_context_data(**kwargs)

        # We convert the queryset to a list so that we can manipulate
        # the model instances in the get() and post() methods
        c['children'] = list(c['page'].get_children().filter(state=5))

        return c

    """
    We override the get() and post() methods so that we can cycle through
    the page children, and if the page is a ``ContactPage`` we should
    add the contact form to that page.

    This allows us to have multiple different types of "contat pages", which
    all should behave in a different manner, but still allows us to put them
    all on the same list page.
    """
    def get(self, *args, **kwargs):
        c = self.get_context_data(**kwargs)
        for p in c['children']:
            if p.template == "website.contactpage":
                p.form = ContactForm()
        return self.render_to_response(c)

    def post(self, *args, **kwargs):
        c = self.get_context_data(**kwargs)

        for p in c['children']:
            if p.template == "website.contactpage":
                if p.slug == self.request.POST.get("page_id"):
                    p.form = ContactForm(self.request.POST)

                    if p.form.is_valid():
                        next = p.contents.get_next_url()
                        p.form.save(p.contents.get_recipients())
                        return http.HttpResponseRedirect(next)

                else:
                    p.form = ContactForm()

        return self.render_to_response(c)


class ContactPageView(PageView):

    def get(self, *args, **kwargs):
        c = self.get_context_data(**kwargs)
        c['form'] = ContactForm()
        return self.render_to_response(c)

    def post(self, *args, **kwargs):
        c = self.get_context_data(**kwargs)
        form = ContactForm(self.request.POST)

        if form.is_valid():
            next = self.page.contents.get_next_url()
            form.save(self.page.contents.get_recipients())
            return http.HttpResponseRedirect(next)

        c['form'] = form
        return self.render_to_response(c)


# Browser Views
class PageSummary(BrowserView):
    """
    This is a simple item that will render a pretty Call to action
    summary link for the selected page.
    """
    browser_id = 'pages'
    title = 'Links to Pages'
    description = 'Call to Action to a Specific Page'
    template_name = 'browsers/_pages.html'

    def get_items(self, request):
        return Page.objects.published()


class EntrySummary(BrowserView):
    browser_id = 'blog_entries'
    title = "Blog Entries"
    description = "Insert a blog entry link"
    template_name = "browsers/_blogentries.html"

    def get_items(self, request):
        return Entry.objects.published()

