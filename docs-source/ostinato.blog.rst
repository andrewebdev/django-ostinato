ostinato.blog
=============

Overview
--------

A blog is a very common application that are installed for most websites
these days. There are a couple of common features that most blogging apps
provide, but the use cases of every project can be quite different.

Because of this, we decided to bundle a simple skeleton for building your
own blog, and this is what ``ostinato.blog`` does.


How to use ``ostinago.blog``
----------------------------

Start by creating your own blogging application, and with your
own model for the blog entries. This model should subclass
``ostinato.blog.models.BlogEntryBase``.


.. code-block:: python

    from ostinato.blog.models import BlogEntryBase

    class Entry(BlogEntryBase):
        pass


``BlogEntryBase`` provides the following fields for your ``Entry`` Model.


.. code-block:: python

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    state = models.CharFiield(default='private')
    author = models.ForeignKey(User)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    publish_date = models.DateTimeField(null=True, blank=True)
    archived_date = models.DateTimeField(null=True, blank=True)

    allow_comments = models.BooleanField(default=True)


Those are the most basic fields that any blog entry might require, but of course
you can extend this to include any other fields that you may require.


.. code-block:: python

    from ostinato.blog.models import BlogEntryBase

    class Entry(BlogEntryBase):
        contributors = models.ManyToManyField(User, null=True, blank=True)
        preview_image = models.Imagefield(upload_to='uploads', null=True, blank=True)


So now you have a blog entry with two extra fields.


Blog Entry Workflows and Statemachine
-------------------------------------

The blog entries use the statemachine in
`ostinato.blog.workflow.BlogEntryWorkflow`. This is a standard publication
statemachine that has the option for a editor to review a entry before it's
published.


Using the custom manager
------------------------

``Entry.objects.published()`` - Returns a queryset containing published blog
entries


Wrapping up
-----------

Since blogs can vary in use case so much, we have decided to provide only
the bare minimum to get you going and you still need to create your own urls,
views and templates.

The reason for this approach is that we still wish to maintain flexability,
and we feel that this is the best way to approach this.
