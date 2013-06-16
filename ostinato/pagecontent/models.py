from django.db import models
from mptt.fields import TreeForeignKey
from ostinato.pages.models import Page, PageContent


class MetaContent(PageContent):
    """
    This model serves as both an example, and as a default page content
    model that can be added to any templates. It contains some common fields
    that most CMS's require in some way.
    """
    seo_keywords = models.CharField(max_length=250, null=True, blank=True)
    seo_description = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class ContactFormContent(PageContent):
    recipients = models.TextField(
        help_text="A comma separated list of recipient emails")
    email_subject = models.CharField(max_length=250)
    success_page = TreeForeignKey(
        Page, related_name='redirected_from_set',
        help_text="The page to show the user once the form was succesfully submitted")

    def get_next_url(self):
        return self.success_page.get_absolute_url()

    def get_recipients(self):
        return [i for i in self.recipients.replace(' ', '').split(',')]


# TODO: Bundle RichContent model here that will make use of TinyMCE
