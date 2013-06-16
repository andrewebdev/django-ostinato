from django.db import models

from mptt.fields import TreeForeignKey
from ostinato.pages.models import Page, PageContent


class RichContent(PageContent):
    content = models.TextField(null=True, blank=True)

    class ContentOptions:
        form = 'website.forms.RichContentForm'


class ContactFormContent(PageContent):
    recipients = models.TextField(
        help_text="A comma separated list of recipient emails")
    email_subject = models.CharField(max_length=250)
    success_page = TreeForeignKey(
        Page, related_name='redirected_from_set',
        help_text="The page to show the user once the form was succesfully submitted")

    class ContentOptions:
        form = 'website.forms.ContactPageForm'

    def get_next_url(self):
        return self.success_page.get_absolute_url()

    def get_recipients(self):
        return [i for i in self.recipients.replace(' ', '').split(',')]
