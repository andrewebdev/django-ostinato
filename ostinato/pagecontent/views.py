from django import http
from ostinato.pages.views import PageView
from ostinato.pagecontent.models import ContactFormContent
from ostinato.pagecontent.forms import ContactForm


class ContactPageView(PageView):

    def get(self, *args, **kwargs):
        c = self.get_context_data(**kwargs)
        c['form'] = ContactForm()
        return self.render_to_response(c)

    def post(self, *args, **kwargs):
        c = self.get_context_data(**kwargs)
        form = ContactForm(self.request.POST)

        if form.is_valid():
            content = ContactFormContent.objects.filter(page=self.page)[0]
            next = content.get_next_url()
            form.save(content.get_recipients())
            return http.HttpResponseRedirect(next)

        c['form'] = form
        return self.render_to_response(c)
