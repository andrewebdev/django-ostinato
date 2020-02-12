ostinato.contentbrowser
=======================

The contentbrowser app allows the developer to create browsable resources of any
type available to the admin. When a user opens the contentbrowser for a specific
field, they can then insert a resource into the field in question.

The developer has control over the display and action to take when the user
chooses a resource from the browser. This does mean some extra work for a
developer to set up individual browsers; But it also means a much better
experience for the user adding content in the admin.

If any of the steps below isn't 100% clear, please feel free to have a look
at the demo site for a bit of clarity.


Add ``ostinato.contentbrowser`` to your project
-----------------------------------------------

First we need to add the app to your ``INSTALLED_APPS``.

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'ostinato',
        'ostinato.contentbrowser',
        ...
    )



Creating a browser
------------------
We need to create browser views for every resource we want to make available to
the contentbrowser.

A browser is essentially just a class based view which subclasses
``ostinato.contentbrowser.views.BrowserView``, and renders a list of custom
resource elements.

The view has a couple of custom properties that provide some meta information
to the contentbrowser.

You have to implement a ``get_items`` method for this view. This method should
return a list of resource items for your browser view.


.. code-block:: python

    from django.contrib.auth.models import User
    from ostinato.contentbrowser.views import BrowserView


    class UserCard(BrowserView):
        browser_id = "user_card"
        title = "User detail cards"
        description = "User card that contains user name and email"
        template_name = "browsers/user_cards.html"

        def get_items(self, request):
            return User.objects.filter(is_staff=True).values(
                'id', 'first_name', 'last_name', 'email')


Next we need to create the ``browsers/user_cards.html`` template that will
render the view above.

The view passes the list of items into the template context as ``item_list``.

.. We've also provided custom HTML elements to assist in rendering the resources.
   A textarea is used to specify the actual render template that you want to use
   for the actual resource on the front-end of your site.

  .. note::
      This will most probably change in future to use ``<template>`` but in this
      initial version this is sufficient and works.


.. code-block:: html

    {% for user in item_list %}
    <cb-item browser="{{ browser }}" item="{{ user.id }}" field-namee="{{ field_name }}">
        {{ user.first_name }}

        <textarea name="renderTemplate">
        <div class="userCard">
            <p>{{ user.first_name }} {{ user.last_name }}</p>
            <p><a href="mailto:{{ user.email }}">{{ user.email }}</a></p>
        </div>
        </textarea>
    </cb-item>
    {% endfor %}


The textarea is automatically hidden in the browser. When a user selects any
item in the browser, ``contentbrowser`` will then copy that code and paste it
into the field with ``field_name``.

Now that we have our browser view and template, we need to register this with
the contentbrowser in our ``settings.py``.

.. code-block:: python

    OSTINATO_CONTENTBROWSER = {
        'browsers': [
            'myapp.views.UserCard',
        ]
    }


Almost done now. We need to let django know which form fields it can use the
browser for. ``ostinato.contentbrowser.widgets`` provides a widget mixin,
``CBWidgetMixin`` to use as a mixin on any other widgets.

Lets say we want to add a browser to the
``django.contrib.flatpages`` app.

