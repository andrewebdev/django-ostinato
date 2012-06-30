from django.db import models
from django.contrib.auth.models import User

from ostinato.blog.managers import BlogEntryManager
from ostinato.blog.workflow import BlogEntryWorkflow


class BlogEntryBase(models.Model):
    """
    Our abstract BlogEntryBase model. Using an abstract class allows the
    developer to customize his blog entry models how he/she feels best
    fits the needs of a project.
    """

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True,
        help_text="A unique, url-friendly slug based on the title")
    content = models.TextField()

    # Publication Fields
    state = models.IntegerField(default=1, choices=BlogEntryWorkflow.get_choices())
    author = models.ForeignKey(User)
    
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)
    archived_date = models.DateTimeField(null=True, blank=True)

    allow_comments = models.BooleanField(default=True)

    objects = BlogEntryManager()

    class Meta:
        abstract = True
        ordering = ('-publish_date', '-created_date')
        get_latest_by = 'publish_date'
        permissions = BlogEntryWorkflow.get_permissions()

    def __unicode__(self):
        return '%s' % self.title

