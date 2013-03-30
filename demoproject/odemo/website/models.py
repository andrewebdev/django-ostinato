from django.db import models

from ostinato.pages.models import PageContent
from ostinato.pages.registry import page_content


@page_content.register
class HomePage(PageContent):
    content = models.TextField()


@page_content.register
class GenericPage(PageContent):
    content = models.TextField()