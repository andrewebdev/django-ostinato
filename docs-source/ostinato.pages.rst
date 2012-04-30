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

Ok so earlier we created a custom PageContent model, and gave it a template.
I'm going to assume you've already created that template. Lets see how we can
access the content in the template.

The page view adds ``page`` to your context, which is the current page instance.
Using that it's very easy to do something like this:

.. code-block:: html

    {{ page.title }}


That's all fine, but we have content for a page as well, which is stored in
a different model. There are two ways we can access this content.

1. *The Verbose way* - We can use the related name that points to the content
model. The related name is in the format of, ``<app_label>_<model>_content``.

.. code-block:: html

    <img src="{{ page.myapp_attributionpage_content.preview_image.url }}" />
    {{ page.myapp_attributionpage_content.content }}
    <p>Thanks to, {{ page.myapp_attributionpage_content.attribution }}</p>

This works, but wow that's a lot of typing. Good that we provide a shortcut for
you.

2. *The short way* - We include a field on the page called ``contents``, which
will do the related lookup for you.

.. code-block:: html

    <img src="{{ page.contents.preview_image.url }}" />
    {{ page.contents.content }}
    <p>Thanks to, {{ page.contents.attribution }}</p>

A lot better, no?


Creating a custom view for your content
---------------------------------------

There are cases that you may want to have a custom view to render your template,
rather than just using the default view that ``ostinato.pages`` uses.

One use case for this may be that one of your pages can have a contact form.
So you will need a way to add this form to the page context. You also want this
page to handle the post request etc.

First you create your view. Note that ``ostinato.pages`` makes use of django's
class based views. If you haven't used them before, then it would help to read
up on them.

.. code-block:: python

    from ostinato.pages.views import PageView

    class ContactView(PageView):  ## Note we are subclassing PageView

        def get(self, *args, **kwargs):
            c = self.get_context_data(**kwargs)
            c['form'] = ContactForm()
            return self.render_to_response(c)

        def post(self, *args, **kwargs):
            c = self.get_context_data(**kwargs)
            ## Handle your form ...
            return http.HttpResponseRedirect('/some/url/')

In the example above, we created our own view that will add the form to the
context, and will also handle the post request. There is nothing special here.
It's just the standard django class based views in action.

One thing to note is that our ``ContactView`` inherrits from ``PageView``
(which in turn inherrits from ``TemplateView``). You dont *have* to inherrit
from PageView, but if you dont, then you need to add the ``page`` instance
to the context yourself, whereas ``PageView`` takes care of that for you.

Ok, now we have our view, we need to tell the relative page content model to
use this view when it's being rendered. We do this on the model.

Using our ``AttributionPage`` example from earlier, we change it like so:

.. code-block:: python
    :linenos:
    :emphasize-lines: 11

    from django.db import models
    from ostinato.pages.models import PageContent

    class AttributionPage(PageContent):  ## Note the class inheritance
        preview_image = models.ImageField(upload_to='/previews/')
        content = models.TextField()
        attribution = models.CharField(max_length=150)

        class ContentOptions:
            template = 'attribution_page.html'
            view = 'myapp.views.ContactView'  ## Full import path to your view

See line 11, that's all you need!


Creating complex page content with mixins
-----------------------------------------

Sometimes you may have two different kinds of pages that share other fields.
Lets say for example we have two or more pages that all needs to update our
meta title and description tags for SEO.

It is a bit of a waste to have to add those two fields to each of our content
models manually, not to mention that it introduces a larger margin for errors.

We use mixins to solve this:

.. code-block:: python
    :linenos:

    from django.db import models
    from ostinato.pages.models import PageContent

    class SEOContentMixin(models.Model):  ## Note it's a standard model...
        keywords = models.CharField(max_length=200)
        description = models.TextField()

        class Meta:
            abstract = True  ## ...and _must_ be abstract


    class AttributionPage(SEOContentMixin, PageContent):
        preview_image = models.ImageField(upload_to='/previews/')
        content = models.TextField()
        attribution = models.CharField(max_length=150)

        class ContentOptions:
            template = 'attribution_page.html'
            view = 'myapp.views.ContactView'  ## Full import path to your view

The two points you have to be aware of here:

#. The mixin should be a normal django model

#. The mixin *must* be abstract


Template tags and filters
-------------------------

``ostinato.pages`` comes with a couple of tempalate tags and filters to
help with some of the more common tasks.

**navbar(for_page=None)**

A inclusion tag that renders the navbar, for the root by default. It will render
all child pages for the node. This tag will only render pages that has
``show_in_nav`` selected and is published.

.. code-block:: html

    {% load pages_tags %}

    {% navbar %}

This inclusion tag uses ``pages/navbar.html`` to render the nav, just in case
you want to customize it.

This inclusion tag can also take a extra arument to render the children for a
specific page.

.. code-block:: html

    {% load pages_tags %}

    {% navbar for_page=page %}


**get_page(slug)**

A simple tag that will get a page by the slug, and add it to the context.

.. code-block:: html
    
    {% load pages_tags %}

    {% get_page 'page-1' as mypage %}
    <h1>{{ mypage.title }}</h1>

