The Demo Project
================

Ostinato comes with a demo project that you can use to play around with the app.
The test project uses ``docker`` and ``docker-compose``, which lets you install
and run the entire demo, including all dependencies, in an isolated environment.


If you have both docker and docker-compose installed you can just run:

``docker-compose up``


Running management commands
---------------------------

Any management commands will need to be run through docker-compose as well.
To run syncdb for example just run: ``docker-compose run demo python manage.py
syncdb``. Familiarity with docker and docker-compose will be really helpful.


What's provided in the Demo Site
--------------------------------

Very basic examples of how to use various ostinato apps is included in the
demo site. This includes the following:

* Examples of how to create your own pages template models and register them
* Various uses of the pages app template tags, custom views, admin inlines etc.
* A example of how to use the blog application to create a custom blog for the
  site. Included is a example of how a custom page template can be registered
  for a blog landing page, with custom settings for said page.
* A example of how to create custom content browsers, register them and how to
  use these in the admin.
* Content filters are used in the demo as well.
* Media library usage and implementation in the pages.

Since this is just a demo, we've not bothered with fancy styling for
the demo site since we felt that people might think that certain design features
used in the demo are included with ostinato, and we wanted to avoid this
confusion.
