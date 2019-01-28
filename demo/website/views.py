from django import http
from django.views.generic import TemplateView

from ostinato.pages.views import PageView
from ostinato.pages.models import Page
from ostinato.contentbrowser.views import BrowserView

from website.models import Video, Image
from website.forms import ContactForm
from blog.models import Entry


class ServiceWorkerView(TemplateView):
    """
    Returns dynamically generated javascript file
    """
    template_name = "service-worker.js"
    content_type = "application/javascript"

    def get_context_data(self, **kwargs):
        c = super(ServiceWorkerView, self).get_context_data(**kwargs)
        # Create a flat list of pages which we want to cached
        c['pages'] = Page.objects.published()
        c['latest_entry'] = Entry.objects.filter(state='published').latest('publish_date')
        return c


class TopLevelListPageView(PageView):
    xhr_template_name = 'pages/top_level_list_page_xhr.html'

    def get_context_data(self, **kwargs):
        c = super(TopLevelListPageView, self).get_context_data(**kwargs)

        # We convert the queryset to a list so that we can manipulate
        # the model instances in the get() and post() methods
        c['children'] = list(c['page'].get_children().filter(state='public'))

        return c


class ContactPageView(PageView):
    xhr_template_name = 'pages/contact_page_xhr.html'

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


class VideoBrowser(BrowserView):
    browser_id = 'videos'
    title = 'Videos'
    description = "Insert a video from the media library"
    template_name = "browsers/videos.html"

    def get_items(self, request):
        return Video.objects.visible()


class ImageBrowser(BrowserView):
    browser_id = "images"
    title = 'Images'
    description = "Insert a Image"
    template_name = "browsers/images.html"

    def get_items(self, request):
        return Image.objects.visible()
