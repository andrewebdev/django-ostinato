import time

from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives


class benchmark(object):
    """
    A simple benchmarking class borrowed from:
    http://dabeaz.blogspot.co.uk/2010/02/context-manager-for-timing-benchmarks.html
    """
    def __init__(self,name):
        self.name = name

    def __enter__(self):
        self.start = time.time()

    def __exit__(self,ty,val,tb):
        end = time.time()
        print("%s : %0.3f seconds" % (self.name, end-self.start))
        return False


class Emailer(object):
    """
    A simple class to take care of some repetative code that I end up
    writing for almost every project.
    """
    def __init__(self, **kwargs):
        self.recipients = kwargs['recipients']
        self.from_address = kwargs['from_address']
        self.subject_template = kwargs['subject_template']
        self.body_template = kwargs['body_template']
        self.context = kwargs['context']
        self.bcc = kwargs.get('bcc', None)

    def get_context(self):
        return self._context

    def set_context(self, context={}):
        if 'site' not in context:
            context['site'] = Site.objects.get_current()
        self._context = context

    context = property(get_context, set_context)

    def render(self, template):
        return render_to_string(template, self.context)

    def send(self, as_html=False):
        subject = self.render(self.subject_template).replace('\n', ' ')
        html_content = self.render(self.body_template)
        text_content = strip_tags(html_content)

        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(
            subject, text_content, self.from_address, self.recipients,
            bcc=self.bcc)
        if as_html:
            msg.attach_alternative(html_content, "text/html")

        msg.send()
