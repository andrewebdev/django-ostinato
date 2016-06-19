from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


# TODO: This is a very handy class, should we include in ostinato?
class Emailer(object):

    def __init__(self, **kwargs):
        self.recipients = kwargs['recipients']
        self.from_address = kwargs['from_address']
        self.subject_template = kwargs['subject_template']
        self.body_template = kwargs['body_template']
        self.context = kwargs['context']

    def get_context(self):
        return self._context

    def set_context(self, context={}):
        if 'site' not in context:
            context['site'] = Site.objects.get_current()
        self._context = context

    context = property(get_context, set_context)

    def render(self, template):
        return render_to_string(template, self.context)

    def send(self, attach_html=False):
        subject = self.render(self.subject_template).replace('\n', '')
        html_content = self.render(self.body_template)
        text_content = strip_tags(html_content)

        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(
            subject, text_content, self.from_address, self.recipients)
        if attach_html:
            msg.attach_alternative(html_content, "text/html")

        msg.send()
