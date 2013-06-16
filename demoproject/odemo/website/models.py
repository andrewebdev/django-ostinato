from django.db import models
from ostinato.pages.models import PageContent


class RichContent(PageContent):
    content = models.TextField(null=True, blank=True)

    class ContentOptions:
        form = 'website.forms.RichContentForm'
