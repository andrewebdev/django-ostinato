ostinato.pages
==============

*For the user -*
Allows for creating and publish a hierarchy of pages on the site.

*For the Developer -*
Allows for creating custom content models for pages, which is represented as
a selection of templates. This gives developer more control over custom fields
on a page in a way that can easilly fit into database migrations etc.


A quick overview
----------------

**Pages**

In our pages app, a Page is nothing more than a container for content.
A Page does have some of it's own field and attributes mostly to control
publication and page state

**Page Content**

Page Content is a seperate model from pages, and this is the actual content
for the page. Two of these models already exist within `ostinato.pages`, and
you are free to use them out-of-the-box, but you can easilly create your own if
you need more control over content in your pages.


Requirements
------------

* django-mptt


Add ``ostinato.pages`` to your project
-----------------------------------------

Start by adding the app to your ``INSTALLED_APPS``

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'ostinato.admin',  # Make sure that this is before the django admin
        ...
        'django.contrib.admin',
        ...
        'ostinato.pages',
        'mptt',  # Make sure that mptt is after ostinato.pages
        ...
    )

Now add the ``ostinato.pages.urls`` to the *end* of your urlpatterns so that it
doesn't take priority over your other urlpatterns.

.. code-block:: python

    urlpatterns += [path('', include('ostinato.pages.urls'))]


*Remember* to run ``python manage.py migrate`` after you've done this.

That's it, you now have a basic Pages app. We cannot do anything with it yet,
since we first need to create actual templates and content. We'll do this
in the next section.


Creating and registering page content
-------------------------------------

Ok, so lets say the client you determined that the client needs 2 page
templates:

1. A landing page template that contains a small ``intro`` and text ``content``.
2. A generic page that contains only text ``content``.

We just create these as standard models.

.. code-block:: python
    :linenos:

    from django.db import models
    from ostinato.pages.models import PageContent


    class LandingPage(PageContent):
        intro = models.TextField()
        content = models.TextField()


    class GeneralPage(PageContent):
        content = models.TextField()


As you can see, these are standard django models, except that we inherit from
``ostinato.pages.models.PageContent``.

.. note::
    Since the content you just created are django models, you need to
    remember to run syncdb.

Now we need to register our page content models with the pages app so that it
knows to use them as templates.

In your `settings.py` add the following:

.. code-block:: python
    :linenos:

    OSTINATO_PAGES = {
        'templates': {
            'app.landingpage': {
                'label': 'Landing Page'
            },
            'app.genericpage': {
                'label': 'Generic Page',
            },
        }
    }

Each template basically consists of the django content type identifier used as
the key in this dictionary, with he value specifying custom options for the
template. The key used must be a valid type otherwise we won't know where to
find the model for your template.

If you load up the admin now, you will be able to choose a template for the
page.


Displaying page content in the UI templates
-------------------------------------------

By default the template used by the page is determined by the page content.
The default template location is ``pages/<content_type>.html``.
So, assuming you placed your page models in `myapp.models` the templates for our
two content models (which you'll need to create now) are:

* ``pages/myapp_landingpage.html``
* ``pages/myapp_generalpage.html``

.. note::
    You can override these templates by using the template options setting eg.

    .. code-block:: python

        OSTINATO_PAGES = {
            'templates': {
                'app.landingpage': {
                    'label': 'Landing Page'
                    'template': 'pages/landing_page.html'
                },
                'app.genericpage': {
                    'label': 'Generic Page',
                    'template': 'pages/generic_page.html'
                },
            }
        }


Lets see how we can access the content in the template.

The page view adds ``page`` to your context, which is the current page instance.
Using that it's very easy to do something like this:


.. code-block:: html

    <h1>{{ page.title }}</h1>
    <p class="byline">Published on: {{ page.publish_date }}</p>


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
(which in turn inherits from django's ``TemplateView``). You don't *have* to
inherit from PageView, but if you don't, then you need to add the ``page``
instance to the context yourself, whereas ``PageView`` takes care of that for
you.

We now need to tell the pages app that we want to use a custom view for this
page template. We'll do that by editing the template options.

Continuing from the previous settings, we'll add the custom view.

.. code-block:: python
    :linenos:
    :emphasize-lines: 6

    OSTINATO_PAGES = {
        'templates': {
            'app.landingpage': {
                'label': 'Landing Page'
                'template': 'pages/landing_page.html'
                'view': 'myapp.views.ContactView',  # Full import path to your view
            },
            'app.genericpage': {
                'label': 'Generic Page',
                'template': 'pages/generic_page.html'
            },
        }
    }


Custom forms for Page Content
-----------------------------

``ostinato.pages`` also allows you to specify a custom form for the admin view
for your page content.
You do this in the template options as before:

.. code-block:: python
    :linenos:
    :emphasize-lines: 7

    OSTINATO_PAGES = {
        'templates': {
            'app.landingpage': {
                'label': 'Landing Page'
                'template': 'pages/landing_page.html'
                'view': 'myapp.views.ContactView',
                'admin_form': 'myapp.forms.CustomForm',
            },
            'app.genericpage': {
                'label': 'Generic Page',
                'template': 'pages/generic_page.html'
            },
        }
    }


As you can see we just added that at the end. Just create your custom form
on the import path you specified, and the admin will automatically load the
correct form for your page content.


Custom Statemachine for Pages
-----------------------------

``ostinato.pages.workflow`` provides a default statemachine that is used by
the page model. Sometimes, you may want to create a different workflow for
the pages based on client requirements.

To do this, you just create your custom statemachine as mentioned in the
``ostinato.statemachine`` documentation, and then tell ``ostinato.pages`` which
class to use by changing the `workflow_class` setting for `OSTINATO_PAGES`:


.. code-block:: python
    :linenos:

    OSTINATO_PAGES = {
      # ... other options ...
      'workflow_class': 'ostinato.pages.workflow.PageWorkflow'
    }


Extra Inline Fields for a Page in the Admin
-------------------------------------------

There are cases where you want a specific page to have extra inline fields,
based on the chosen template. We have provided you with this capability through
the template options setting.

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


Now Lets say that we want to add contributors to our ``LandingPage`` from
earlier:


.. code-block:: python
    :linenos:
    :emphasize-lines: 8-10


    OSTINATO_PAGES = {
        'templates': {
            'app.landingpage': {
                'label': 'Landing Page'
                'template': 'pages/landing_page.html'
                'view': 'myapp.views.ContactView',
                'admin_form': 'myapp.forms.CustomForm',
                'page_inlines': [
                    'myapp.admin.ContributorInline'
                ]
            },
            'app.genericpage': {
                'label': 'Generic Page',
                'template': 'pages/generic_page.html'
            },
        }
    }


If you load up the django admin now, and edit a Landing Page, you should see
the extra inline model fields below your PageContent.

To access the related set in your template, just do it as normal.

.. code-block:: html

    {% for contributor in page.contributor_set.all %}
      {{ contributor.name }}
    {% endfor %}


Template tags and filters
-------------------------

``ostinato.pages`` comes with a couple of tempalate tags and filters to
help with some of the more common tasks.


**breadcrumbs(for_page=None, obj=None)**

This tag will by default look for ``page`` in the context. If found it will
render the breadcrumbs for this page's ancestors.

.. code-block:: html

    {% load pages_tags %}
    {% breadcrumbs %}


If you want to manually specify the page for which to render the breadcrumbs,
you can do that using ``for_page``.

.. code-block:: html

    {% load pages_tags %}
    {% breadcrumbs for_page=custom_page %}


Sometimes you may have a object that does not belong to the standard page
hierarchy. This could be a model like a BlogEntry, but when viewing the detail
template for this entry, you may still want to relate this object to a page.
For this you can use ``obj``.

.. code-block:: html

    {% load pages_tags %}
    {% breadcrumbs for_page=blog_landingpage obj=entry %}


One thing to note about the custom object is that the model must have a
``title`` attribute, and a ``get_absolute_url()`` method.


**filter_pages(**kwargs)**

This tag will filter the pages by ``**kwargs`` and return the the queryset.

.. code-block:: html

    {% load pages_tags %}
    {% filter_pages state=5 as published_pages %}
    {% for p in published_pages %}
        <p>{{ p.title }}</p>
    {% endfor %}

**get_page(**kwargs)**

Same as ``filter_pages``, except that this tag will return the first item
found.

.. code-block:: html

    {% load pages_tags %}
    {% get_page slug='page-1' as mypage %}
    <h1>{{ mypage.title }}</h1>


Pages Settings
--------------

.. code-block:: python

    OSTINATO_PAGES_SETTINGS = {
        # Ostinato uses django caching to reduce database hits for things like
        # retrieving the page urls, breadcrumbs etc. This settings is used to
        # specify what cache name to use.
        'cache_name': 'default',

        'cache_key_separator': ':',

        # The default state for pages in the pages statemachine.
        # This must be a valid state in for the statemashine used by the pages
        # app. If you specify your own workflow_class below, then you need to
        # ensure that default_state is correct.
        'default_state': 'public',

        # Specify a custom statemachine and wokflow via this override.
        # The value is the full import path to the main workflow class
        'workflow_class': 'ostinato.pages.workflow.PageWorkflow',

        # Your custom template options
        'templates': { }
    }
