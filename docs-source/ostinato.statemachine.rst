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

[insert uml state diagram here]


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

    from ostinato.statemachine import State, StateMachine

    class Private(State):
        verbose_name = 'Private'
        transitions = {'publish': 'public'}

    class Public(State):
        verbose_name = 'Public'
        transitions = {'retract': 'private', 'archive': 'archived'}

    class Archived(State):
        verbose_name = 'Archived'
        transitions = {}


This is simple enough. Every state is a subclass of
``ostinato.statemachine.core.State`` and each of these states specifies two
attributes.

* ``verbose_name`` is just a nice human readable name.

* ``transitions`` is a dict where the *keys* are transition/action names, and
    the *values* is the target state for the transition.

Now we have to glue these states together into a statemachine.


.. code-block:: python
    :linenos:

    class NewsWorkflow(StateMachine):
        state_map = {'private': Private, 'public': Public, 'archived': Archived}
        initial_state = 'private'


* ``state_map`` is a dict where *keys* are unique id's/names for the states;
    *values* are the actual ``State`` subclass

* ``initial_state`` is the starting state *key*

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
    >>> sm.state
    'Public'

    # We can view available actions based on the current state
    >>> sm.actions
    ['retract', 'archive']

    # We can tell the statemachine to take action
    >>> sm.take_action('retract')

    # State is now changed in the statemachine ... 
    >>> sm.state
    'Private'

    # ... and we can see that our original instance was also updated.
    >>> item.state
    'private'
    >>> item.save()  # Now we save our news item


Action methods
--------------
You can create custom *action methods* for states, which allows you to do
extra stuff, like updating the publish_date.

Our example ``NewsItem`` already has a empty ``publish_date`` field, so lets
create a method that will update the publish date when the ``publish`` action
is performed.


.. code-block:: python
    :linenos:

    from django.utils import timezone

    class Private(State):
        verbose_name = 'Private'
        transitions = {'publish': 'public'}

        def publish(self, **kwargs):
            if self.instance:
            self.instance.publish_date = timezone.now()


Now, whenever the ``publish`` action is called on our statemachine, it will
update the ``publish_date`` for the instance that was passed to the
``StateMachine`` when it was created.

.. note::

    The name of the method is important. The ``State`` class tries to look
    for a method with the same name as the ``transition`` *key*.

    You can use the ``kwargs`` to pass extra arguments to your custom methods.
    These arguments are passed through from the ``StateMachine.take_action()``
    method eg.

    .. code-block:: python

        sm.take_action('publish', author=request.user)

