
class InvalidTransition(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class State(object):
    verbose_name = None
    transitions = {}
    permissions = (
        ('view', 'Can View'),
        ('edit', 'Can Edit'),
        ('delete', 'Can Delete'),
    )


    def __init__(self, instance=None, **kwargs):
        self.instance = instance
        self.extra_args = kwargs


    def set_state(self, new_state):
        """
        A method that can be overridden for custom state processing.
        By default this method looks for a ``state_field`` on the instance
        and just updates that field.
        """

        if self.instance:
            state_field = self.extra_args.get('state_field', 'state')
            setattr(self.instance, state_field, new_state)

        return new_state


    def transition(self, action, **kwargs):
        """
        Performs a transition based on ``action`` and returns a
        instance for the next State
        """
        try:
            new_state = self.transitions[action]
        except KeyError:
            raise InvalidTransition('%s is not a valid action. Valid actions '\
                'are: %s' % (action, [k for k in self.transitions]))
        
        # Try to run a custom method if it exists
        if hasattr(self, action):
            getattr(self, action)(**kwargs)

        return self.set_state(new_state)


class StateMachine(object):
    state_map = {}
    initial_state = ''


    def __init__(self, instance=None, **kwargs):
        """
        The entry point for our statemachine.

        ``kwargs`` is extra arguments that the developer can pass through
        to the statemachine and it's States.
        This can then be used in the custom action methods for those states.
        """
        self.instance = instance
        self.extra_args = kwargs
        self.process_state()


    def set_state(self, state):
        self._state = state

    def get_state(self):
        return self.state_map[self._state].verbose_name

    state = property(get_state)


    def get_actions(self):
        return [i for i in self.get_state_instance().transitions]

    actions = property(get_actions)


    @classmethod
    def get_choices(cls):
        """
        Returns a standard django tuple containing a list of States, in
        the format, ``(<state_value>, '<verbose_name>')``.

        This is a handy helper for using in django choices fields etc.
        """
        choices = ()
        for k in cls.state_map:
            choices += ((k,
                cls.state_map[k].verbose_name or cls.state_map[k].__name__),)

        return choices


    def process_state(self):
        """
        Our default state processor. This method can be overridden
        if the state is determined by more than just a field on the
        instance.

        If you override this method, make sure to call set_state() to
        set the state on the instance.
        """
        self.state_field = self.extra_args.get('state_field', 'state')

        state = self.extra_args.get('state', None)
        if not state:
            state = getattr(self.instance, self.state_field, None)\
                    or self.initial_state

            if state not in self.state_map:
                state = self.initial_state

        self.set_state(state)


    def get_state_instance(self):
        """ Returns a single instance for the current state """
        return self.state_map[self._state](
            instance=self.instance, **self.extra_args)


    def take_action(self, action, **kwargs):
        self._state = self.get_state_instance().transition(action, **kwargs)


    def action_result(self, action):
        """
        Determines what the resulting state for would be if ``action`` is
        transitioned.
        """
        try:
            return self.get_state_instance().transitions[action]
        except KeyError:
            raise InvalidTransition('%s, is not a valid action.' % action)

    @classmethod
    def get_permissions(cls):
        """
        Returns the permissions for the different states and transitions
        as tuples, the same as what django's permission system expects.
        """
        perms = ()

        for k, v in cls.state_map.iteritems():
            for perm in v.permissions:
                perms += ((
                    '%s_%s' % (v.__name__.lower(), perm[0]),
                    '[%s] %s' % (v.__name__, perm[1])
                ),)

            # Now add the transition permissions
            for t in v.transitions:
                perm = ('can_%s' % t, 'Can %s' % t.capitalize())
                if perm not in perms:  # Dont add it if it already exists
                    perms += (perm,)

        return perms


class IntegerStateMachine(StateMachine):

    def set_state(self, state):
        super(IntegerStateMachine, self).set_state(int(state))

