ostinato.contentfilters
=======================

The ``ostinato.contentfilters`` app provides you with a easy way to apply a
list of filters to content, which is rendered in your templates. The basic
functionality is the same as standard django template filters, except that
they are appllied as a group. This is handy if you want to apply a whole range
of filters to a single piece of content.

We also include a couple of filters for some common use cases.


Writing a Contentfilter
-----------------------
Start by creating a standard django template tag library. In our case we will
call this ``custom_filters.py``.

.. code-block:: python

    from django import template
    register = template.Library()


Now we need to create our filter. For this example we will create a simple
filter that will convert the content to uppercase.

.. code-block:: python

    from django import template
    from ostinato.contentfilters import ContentMod

    register = template.Library()

    def to_upper(content):
        return content.upper()

    ContentMod.register('upper', to_upper)


As you can see you just create a basic function, which takes a single argument,
``content``. You then do some processing on your content, and return the result.

The last thing you need to do is register your modifier with
``ostinato.contentfilters.ContentMod``. The first argument here is the unique
name for the filter. The second argument is the function to use.


Using the filters in your templates
-----------------------------------

Now that you have your content filters registered, you can use them in your
templates.

.. code-block:: html

    {% load content_filters custom_filters %}
    {{ 'some lowercase content'|modify }}


Firstly note that we need to load both template tag libraries for
``content_filters`` and ``custom_filters``.

Secondly you will see we just applied a single ``modify`` filter to our content.
Calling ``modify`` without any arguments will run through *all* registered
filters.

You can apply specific filters by passing it as arguments to ``modify``:


.. code-block:: html
    
    {% load content_filters custom_filters %}
    {{ 'some lowercase content'|modify:"upper,another_filter" }}


You can also tell it to exclude filters. The following will use *all*
registered filters, except for ``upper`` and ``youtube``. Note the exclamation
mark at the start of the filter list.


.. code-block:: html
    
    {% load content_filters custom_filters %}
    {{ 'some lowercase content'|modify:"!upper,another_filter" }}


Default content filters included with ostinato.contentfilters
-------------------------------------------------------------

* ``youtube`` - Searches for a youtube url in the content, and replaces it with
    the html embed code.

* ``snip`` - Searches for a string, ``{{{snip}}}`` in the content, and if found
    it truncates the content at that point.

* ``hide_snip`` - Searches for a string, ``{{{snip}}}`` in the content, and if
    found, removes it from the content.

