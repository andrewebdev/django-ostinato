ostinato.statemachine
=====================

Overview
--------

Ostinato includes a statemachine that will allow you to create complex
workflows for your models. A common workflow, for example, is a publishing
workflow where an item can be either ``private`` or ``public``. The change from
the one state to the next is called a transition.

In ostinato our main aim was to have the ability to "attach" a statemachine
to a model, without having to change any fields on that model. So you can
create your States and StateMachines completely independent of your models,
and just *attach* it when needed.


Ok, lets build an actual statemachine so you can see how it works. For this
example we will create the following statemachine:

.. image:: images/demo_statemachine.png

For our example we will assume you are creating a statemachine for the
following model:


.. code-block:: python

    class NewsItem(models.Model):
        title = models.CharField(max_length=150)
        content = models.TextField()
        publish_date = models.DateTimeField(null=True, blank=True)
        state = models.CharField(max_length=50, default='private')


We start by creating our States...


.. code-block:: python
    :linenos:

    from ostinato.statemachine import State, StateMachine, action

    class Private(State):
        value = 'private'
        verbose_name = 'Private'

        @action('public', verbose_name='Make public')
        def publish(self, **kwargs):
            if self.manager.instance:
                self.manager.instance.publish_date = timezone.now()

    class Public(State):
        verbose_name = 'Public'

        @action('private')
        def retract(self, **kwargs):
            pass

        @action('archived')
        def archive(self, **kwargs):
            pass

    class Archived(State):
        verbose_name = 'Archived'


This is simple enough. Every state is a subclass of
``ostinato.statemachine.core.State`` and each of these states specifies two
attributes.

* ``value`` is the exact, unique, value that represents the state in the
  database.

* ``verbose_name`` is just a nice human readable name.

We also define a couple of actions for the state. The action decorator specifies
which target state value we should transition to after the action method was
executed.

Next we create our statemachine and tell it what states to use.


.. code-block:: python
    :linenos:

    class NewsWorkflow(StateMachine):
        states = (Private, Public, Archived)
        initial_state = Private


* ``states`` is a is a tuple that lists every State class that should be used
  with this statemachine.

* ``initial_state`` The state class to use as the initial state when none is
  present.

Thats all you need to set up a fully functioning statemachine.

Lets have a quick look at what this allows you to do:


.. code-block:: python

    >>> from odemo.news.models import NewsItem, NewsWorkflow

    # We need an instance to work with. We just get one from the db in this case
    >>> item = NewsItem.objects.get(id=1)
    >>> item.state
    u'public'

    # Create a statemachine for our instance
    >>> sm = NewsWorkflow(instance=item)

    # We can see that the statemachine automatically takes on the state of the
    # newsitem instance.
    >>> sm.state.value, sm.state.verbose_name
    'public', 'Public'

    # We can view available actions based on the current state
    >>> sm.actions
    (('retract', 'Retract'), ('archive', 'Archive'))

    # We can tell the statemachine to take action
    >>> sm.transition('retract')

    # State is now changed in the statemachine ...
    >>> sm.state.value
    'private'

    # ... and we can see that our original instance was also updated.
    >>> item.state
    'private'

    >>> item.save()  # Now we save our news item


Define Actions without the decorator
------------------------------------

You can manually create a action in a state without using the action. This can
be handy when your action has logic that can transition to different target
states, depening on other external factors.

.. code-block:: python
    :linenos:

    class Private(State):
        value = 'private'
        verbose_name = 'Private'

        def publish(self, **kwargs):
            if self.manager.instance:
                self.manager.instance.publish_date = timezone.now()

            if something_bad_happened:
                return self.transition_to('review')

            return self.transtion_to('public')
        publish.is_action = True
        publish.verbose_name = 'Make public'


.. note::

    Your manual action must always return the resulting call for
    `self.transition_to`. The value passed to this method is the target state
    value that you would like to transition to.

    When doing a manual declaration, you must set the `is_action` and
    `verbose_name` properties for the related method, as seen in the example
    above.


Admin Integration
-----------------

Integrating your statemachine into the admin is quite simple. You just need to
use the statemachine form factory function that generates the form for your
model, and then use that form in your ModelAdmin.


.. code-block:: python
    :linenos:

    from odemo.news.models import NewsItem, NewsWorkflow
    from ostinato.statemachine.forms import sm_form_factory


    class NewsItemAdmin(admin.ModelAdmin):
        form = sm_form_factory(NewsWorkflow)

        list_display = ('title', 'state', 'publish_date')
        list_filter = ('state',)
        date_hierarchy = 'publish_date'


    admin.site.register(NewsItem, NewsItemAdmin)


Lines 2 and 6 are all that you need. ``sm_form_factory`` takes as it's first
argument your Statemachine Class.


Custom ``state_field``
----------------------

The statemachine assumes by default that the model field that stores the state
is called, ``state``, but you can easilly tell the statemachine (and the
statemachine form factory function) what the field name for the state will be.

* Statemachine - ``sm = NewsWorkflow(instance=obj, state_field='field_name')``

* Form Factory - ``sm_form_factory(NewsWorkflow, state_field='field_name')``

