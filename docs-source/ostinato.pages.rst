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


Requirements
------------

* django-mptt
* django-appregister


Add ``ostinato.pages`` to your project
-----------------------------------------

Start by adding the app to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...

        'ostinato',
        'ostinato.pages',
        'mptt',  # Make sure that mptt is after ostinato.pages

        ...
    )

Now add the ``ostinato.pages.urls`` to the *end* of your urlpatterns. It is
important to add this snippet right at the end of the ``urls.py`` so that pages doesn't take priority over your other urlpatterns. That is of course unless
you want it to, in which case you can add it where-ever you wish.

.. code-block:: python

    urlpatterns += patterns('',
        url(r'^', include('ostinato.pages.urls')),
    )

*Remember* to run ``syncdb`` after you've done this.

That's it, you now have a basic Pages app. We cannot do anything with it yet,
since we first need to create actual templates and content. We'll do this
in the next section.

.. note::

    **Publication and Timezones**

    Django 1.4 changed how timezones are treated. So if you mark a page as
    published, please remember that it is published, relative to the timezone
    you specified in your settings.py.


Creating and registering page content
-------------------------------------

Ok, so lets say the client wants a landing page that contains a small ``intro``
and ``content``, and a general page that contains only ``content``. It was
decided by you that these would all be TextFields.

Lets create these now. You need to place these in your app/project
``models.py``.


.. code-block:: python
    :linenos:

    from django.db import models
    from ostinato.pages.models import PageContent
    from ostinato.pages.regitry import page_content

    @page_content.register
    class LandingPage(PageContent):  # Note the class inheritance
        intro = models.TextField()
        content = models.TextField()

    @page_content.register
    class GeneralPage(PageContent):
        content = models.TextField()


As you can see, these are standard django models, except that we inherit from
``ostinato.pages.models.PageContent``.

You also need to register your model with the ``page_content`` registry, as
you can see on lines 5 and 10.

.. note::
    Since the content you just created are django models, you need to
    remember to run syncdb.

If you load up the admin now, you will be able to choose a template for the
page.


Displaying page content in the templates
----------------------------------------

By default the template used by the page is determined by the page content.
The default template location is ``pages/<content_model_name>.html``.
So the templates for our two content models (which you'll need to create now)
are:

* ``pages/landing_page.html``
* ``pages/general_page.html``

.. note::
    You can override these templates by using the ``ContentOptions`` meta class
    in your page content model.

    .. code-block:: python

        class GeneralPage(PageContent):
            content = models.TextField()

            class ContentOptions:
                template = 'some/custom/template.html'


Lets see how we can access the content in the template.

The page view adds ``page`` to your context, which is the current page instance.
Using that it's very easy to do something like this:


.. code-block:: html

    <h1>{{ page.title }}</h1>
    <p class="byline">Author: {{ page.author }}</p>


That's all fine, but we have content for a page as well, which is stored in
a different model. We include a field on the page called ``contents``, which
will get the related page content for you.

In the following example, we assume that you are editing your
``landing_page.html``.


.. code-block:: html

    <p>{{ page.contents.intro }}</p>
    <p>{{ page.contents.content }}</p>


.. note::

    You can also access the content using the django related field lookups, but
    this method is very verbose and requires a lot of typing. The related name
    is in the format of, ``<app_label>_<model>_content``.

    .. code-block:: html

        <p>{{ page.myapp_landingpage_content.intro }}</p>
        <p>{{ page.myapp_landingpage_content.content }}</p>


Creating a custom view for your content
---------------------------------------

There are cases where you may want to have a custom view to render your
template rather than just using the default view used by ``ostinato.pages``.

One use case for this may be that one of your pages can have a contact form.
So you will need a way to add this form to the page context. You also want this
page to handle the post request etc.

First you create your view. Note that ``ostinato.pages`` makes use of django's
class based views. If you haven't used them before, then it would help to read
up on them.


.. code-block:: python

    from ostinato.pages.views import PageView

    class ContactView(PageView):  # Note we are subclassing PageView

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

One thing to note is that our ``ContactView`` inherits from ``PageView``
(which in turn inherits from ``TemplateView``). You don't *have* to inherit
from PageView, but if you don't, then you need to add the ``page`` instance
to the context yourself, whereas ``PageView`` takes care of that for you.

Next we need to tell the page content model to use this view when it's being
rendered. We do this in the ``ContentOptions`` meta class for the page content.

Using our ``LandingPage`` example from earlier, we change it like so:

.. code-block:: python
    :linenos:
    :emphasize-lines: 9

    from django.db import models
    from ostinato.pages.models import PageContent

    class LandingPage(PageContent):
        intro = models.TextField()
        content = models.TextField()

        class ContentOptions:
            view = 'myapp.views.ContactView'  # Full import path to your view


Custom forms for Page Content
-----------------------------

``ostinato.pages`` also allows you to specify a custom form for page content.
You do this in the ContentOptions class like the example below:

.. code-block:: python
    :linenos:
    :emphasize-lines: 9

    from django.db import models
    from ostinato.pages.models import PageContent

    class LandingPage(SEOContentMixin, PageContent):
        intro = models.TextField()
        content = models.TextField()

        class ContentOptions:
            form = 'myapp.forms.CustomForm'  # Full import path to your form


As you can see we just added that at the end. Just create your custom form
on the import path you specified, and the admin will automatically load the
correct form for your page content.


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

    class SEOContentMixin(models.Model):  # Note it's a standard model...
        keywords = models.CharField(max_length=200)
        description = models.TextField()

        class Meta:
            abstract = True  # ...and _must_ be abstract


    class LandingPage(SEOContentMixin, PageContent):
        intro = models.TextField()
        content = models.TextField()


The two points you have to be aware of here:

#. The mixin should be a normal django model

#. The mixin *must* be abstract


Extra Inline Fields for a Page in the Admin
-------------------------------------------

There are cases where you want a specific page to have extra inline fields,
based on the chosen template. We have provided you with this capability through
the PageContent model.

First you need to create the model that should be related to your page.


.. code-block:: python
    :linenos:

    from django.db import models
    from ostinato.pages.models import Page

    class Contributor(models.Model):
        page = models.ForeignKey(Page)
        name = models.CharField(max_lenght=50)


Next, you need to create your inline class (usually done in admin.py).


.. code-block:: python
    :linenos:

    from django.contrib import admin

    class ContributorInline(admin.StackedInline):
        model = Contributor


Right, after a quick syncdb, we are ready to add this to our page content.
Lets say that we want to add contributors to our ``LandingPage`` from earlier:


.. code-block:: python
    :linenos:
    :emphasize-lines: 8

    ...

    class LandingPage(SEOContentMixin, PageContent):
        intro = models.TextField()
        content = models.TextField()

        class ContentOptions:
            page_inlines = ['myapp.admin.ContributorInline']
    ...

If you load up the django admin now, and edit a Landing Page, you should see
the extra inline model fields below your PageContent.

To access the related set in your template, you can use the queryset that we
provide on the page contents:

.. code-block:: html
    :linenos:
    :emphasize-lines: 2

    {% for contrib in page.contents.contributor_set %}
    {{ contrib.name }}
    {% endfor %}

Note that the variable ``contributor_set`` is a queryset, and *not* a
ManyRelatedManager, so you dont need to add ``.all`` to it.


.. note::

    You can still access this content the usual method by doing a reverse
    lookup on the page instance.
    
    .. code-block:: html
        
        {% for contrib in page.contributor_set.all %}
        {{ contrib.name }}
        {% endfor %}


Extra Inline Fields via a "through" model
-----------------------------------------

In rare cases you may have a complex model that requires extra information
for the relationship. This is normally done in Django via a ManyToManyField()
using the ``through`` argument.

To do this you would specify the inline model, and the name of the field,
as a tuple in the ``page_inlines`` option.

.. code-block:: python
    :linenos:
    :emphasize-lines: 10, 20

    from django.db import models
    from ostinato.pages.models import Page

    class Photo(models.Model):
        image = models.ImageField(upload_to='photos/')

    class Contributor(models.Model):
        page = models.ForeignKey(Page)
        name = models.CharField(max_lenght=50)
        photos = models.ManyToManyField(Photo, through='ContributorPhotos')

    class ContributorPhotos(models.Model):
        photo = models.ForeignKey(Photo)
        contributor = models.ForeignKey(Contributor)

        # Just an arbitary field to justify the example
        order = models.PositiveIntegerField(default=1)

    class ContributorPhotoInline(admin.StackedInline):
        model = Contributor.photos.through


The content options for adding the photos as a inline would be:

.. code-block:: python
    :linenos:
    :emphasize-lines: 8

    ...

    class LandingPage(SEOContentMixin, PageContent):
        intro = models.TextField()
        content = models.TextField()

        class ContentOptions:
            page_inlines = [('myapp.admin.ContributorPhotoInline', 'contributor')]
    ...


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


The ``navbar`` tag also allows has the ability to "discover" a page, based on
the path. This is helpful if you are on a page that isn't a ostinato page, but
a page-slug does exist in the url path, and you want that page to be
highlighted as the active page.

.. code-block:: html
    
    {% load pages_tags %}
    {% navbar path=request.path %}

Note that in the example above, you will need to add the django request
context-processor.


**get_page(slug)**

A simple tag that will get a page by the slug, and add it to the context.

.. code-block:: html
    
    {% load pages_tags %}

    {% get_page 'page-1' as mypage %}
    <h1>{{ mypage.title }}</h1>


