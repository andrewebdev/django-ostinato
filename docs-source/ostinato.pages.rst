ostinato.pages
==============

*For the user -*
Allows for creating a hierarchy of pages, manage publishing, and displaying
the pages in the site's navigation.

*For the Developer -*
Allows for creating custom Content for Pages, which can be customized on a
per-project-basis.

A quick overview
----------------

**Pages**

In our pages app, a Page is nothing more than a container for content.
A Page does have some of it's own field and attributes, but these are mostly
to set certain publication details etc.

**Page Content**

Page Content is a seperate model from pages, and this is the actual content
for the page. Two of these models already exist within pages, and you are free
to use them out-of-the-box, but you can easilly create your own if you need
more control over content in your pages.



Add ``ostinato.pages`` to your project
-----------------------------------------

Start by adding the app to your ``INSTALLED_APPS``

.. code-block:: python

   INSTALLED_APPS = (
       ...

       'ostinato',
       'ostinato.pages',
       'ostinato.statemachine',

       ...
   )

**Note** that we also added ``ostinato.statemachine``. Dont worry about the
specifics, just as long as you know that ``ostinato.pages`` depends on that app,
and you need to have both in your ``INSTALLED_APPS``.

Now add the ``ostinato.pages.urls`` to your *end* of your urlpatterns. If you
are adding the pages urls to the root of your site, it's very important to add
this snippet right at the end of the ``urls.py`` so that pages doesn't take
priority over your other urlpatterns.

.. code-block:: python

    urlpatterns += patterns('',
        url(r'^', include('ostinato.pages.urls')),
    )

*Remember* to run ``syncdb`` after you've done this.

That's it, you now have a basic Pages app. You cannot add content to it yet,
but you can create a hierarchy of pages to define the structure of your site.

Give it a go in the admin. You'll notice that the ``template`` field is a empty
dropdown. We'll be adding Page Content (and templates) in the next section.

Registering page content (templates)
------------------------------------

Ok, now that you've played with the Pages, you can see that there are some basic
things you can do with them, but the pages dont have any fields for entering the
actual content you want to display on the site.

The reason ostinato treats content seperate from the page, is so that *you* have
control over what kind of content you want the user to enter, based on the
page template.

ositnato.pages provides you with 2 PageContent which you can use if all you need
are some basic fields. Lets add those two now.

.. code-block:: python

    OSTINATO_PAGE_TEMPLATES = (
        ('pages.landingpage', 'Landing Page'),
        ('pages.basicpage', 'Basic Page'),
    )

This setting contains a list of PageContent areas, which *also* determines what
templates are available to the pages, hence the name, ``OSTINATO_PAGE_TEMPLATES``.

1. The first part of each "template", is the ``<app_label>.<model>`` codename for the
PageContent model. In this case we are using the ones that are included with
``ostinato.pages``.

2. The second part of the tuple contains a nice human friendly name for the
template.

Right, run your server again, and check the admin, you can now select one of
those two templates for a page. After selecting a template, click
``save and continue...`` and you will see at the bottom of the page the option
to add content to the page.

The two templates have some basic fields. The landing page has introduction and
content text areas, and the basic page only has a content field.

Ok, so what if you need some more control? You want a template that has
something completely different? Head over to the next section.


Creating custom page content
----------------------------

Ok, so lets say the client wants a unique set of pages on the site that contains
a ``preview_image``, ``attribution field`` and a ``text area``?

We will need to create a new ``PageContent`` model first. You can do this in
your project or custom app ``models.py``.

.. code-block:: python
    :linenos:

    from django.db import models
    from ostinato.pages.models import PageContent

    class AttributionPage(PageContent):  ## Note the class inheritance
        preview_image = models.ImageField(upload_to='/previews/')
        content = models.TextField()
        attribution = models.CharField(max_length=150)

        class ContentOptions:
            template = 'attribution_page.html'

Before we register this in our templates, lets go through what we've done.

As you can see, this is a standard django model, except that we inherit from
``ostinato.pages.models.PageContent`` and that we add a new meta class inside
our model called, ``ContentOptions``.

The option, ``template`` in ``ContentOptions`` is the path to the template that
will be used to render your page. You can create that now, or leave it for later.

Ok, now we add this to our ``OSTINATO_PAGE_TEMPLATES``, we will assume you
created the PageContent models in your ``myapp`` application.

.. code-block:: python

    OSTINATO_PAGE_TEMPLATES = (
        ('pages.landingpage', 'Landing Page'),
        ('pages.basicpage', 'Basic Page'),
        ('myapp.attributionpage', 'Page with attribution'),
    )

**Remember**, since the content model you just created is a model, you will need
to run syncdb again.

That's all. Go ahead and test it if you wish.

Displaying page content in the templates
----------------------------------------

tbc ...

