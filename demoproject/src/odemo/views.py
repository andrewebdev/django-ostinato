from django import forms
from django import http

from ostinato.pages.views import PageView


class ContactForm(forms.Form):
    email = forms.CharField()
    message = forms.CharField()

    def save(self):
        print "Sending form..."
        ## but just do nothing, we dont need anything for this test


class ContactView(PageView):

    def get(self, *arsg, **kwargs):
        c = self.get_context_data(**kwargs)
        c['form'] = ContactForm()
        return self.render_to_response(c)

    def post(self, *args, **kwargs):
        c = self.get_context_data(**kwargs)
        form = ContactForm(self.request.POST)

        if form.is_valid():
            form.save()
            return http.HttpResponseRedirect('/about/contact/success/')

        c['form'] = form
        return self.render_to_response(c)
