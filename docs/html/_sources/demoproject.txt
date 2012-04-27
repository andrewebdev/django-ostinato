The Demo Project
================

Ostinato comes with a demo project that you can use to play around with the app.
The test project uses zc.buildout, which lets you install and run the entire
demo, including all dependencies, in an isolated environment.


Setting up the demo project
---------------------------

After checking out or downloading the source, you will see the ``demoproject``
folder. There should be two files in that folder ``bootstrap.py`` and
``buildout.cfg``. The actual django project is in ``demoproject/src/odemo``.

Lets build the project. To do so you bootstrap it using the python version of
your choice.

``python bootstrap.py`` or you could do, ``python2.6 bootstrap.py``. Just
remember that ostinato have not been tested with versions lower than 2.6.

Ok, after the bootstrap, you will see there should now be a ``bin`` folder.

Now run: ``./bin/buildout``

This will start to download django, mptt, an any other dependecies required
for the project to run.

Running the demo project
------------------------

Once the buildout has been created, and is finished. A new file will be in the
``bin`` folder called ``odemo``. This is basically a wrapper for ``manage.py``
that ensures that the project is run within buildout, and not in the system.

So lets sync the database: ``./bin/odemo syncdb

After the sync we can run the dev server: ``./bin/odemo runserver``

