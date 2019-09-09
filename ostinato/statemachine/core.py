from functools import wraps


class StateMachineError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


class InvalidTransition(StateMachineError):
    pass


def action(target_state, verbose_name=None):
    """
    Decorator to be used with state methods. This defines a transtion action
    that will be available for this state.

    @param target_state: The state to transition to when the action is invoked
    @param verbose_name: A verbose name to display this action in the UI. If
    this isn't provided we will use the capitalized method name.
    """
    def decorator(fn):
        fn.target_state = target_state
        if not verbose_name:
            fn.verbose_name = fn.__name__.capitalize()
        else:
            fn.verbose_name = verbose_name

        @wraps(fn)
        def _make_action(self, *args, **kwargs):
            fn(self, *args, **kwargs)
            return self.transition(fn.target_state)

        return _make_action
    return decorator


class State(object):
    value = ''
    verbose_name = None
    permissions = (
        ('view', 'Can View'),
        ('edit', 'Can Edit'),
        ('delete', 'Can Delete'),
    )

    def __init__(self, manager, **kwargs):
        self.manager = manager
        self.extra_args = kwargs

    @classmethod
    def get_actions(cls):
        _actions = ()
        for attr in dir(cls):
            _method = getattr(cls, attr)
            if hasattr(_method, 'target_state'):
                _actions += (
                    (_method.__name__, _method.verbose_name),
                )
        return _actions

    def transition(self, target):
        """
        A method that can be overridden for custom state processing.
        By default this method looks for a ``state_field`` on the instance
        and just updates that field.
        """
        # Get the new instance
        if self.manager.instance:
            state_field = self.extra_args.get('state_field', 'state')
            setattr(self.manager.instance, state_field, target)

        # Fetch the state from the manager
        return self.manager.get_state_by_value(target)


class StateMachine(object):
    states = ()
    initial_state = None
    instance = None
    state = None

    def __init__(self, instance=None, **kwargs):
        """
        The entry point for our statemachine.

        ``kwargs`` is extra arguments that the developer can pass through
        to the statemachine and it's States.
        This can then be used in the custom action methods for those states.
        """
        self.instance = instance
        self.extra_args = kwargs
        self.init_state()

    @property
    def actions(self):
        return self.state.get_actions()

    @classmethod
    def get_choices(cls):
        """
        Returns a standard django tuple containing a list of States, in
        the format, ``(<state_value>, '<verbose_name>')``.

        This is a handy helper for using in django choices fields etc.
        """
        choices = ()
        for state in cls.states:
            choices += (
                (state.value, state.verbose_name or state.__name__),
            )
        return choices

    def get_state_by_value(self, value):
        state = None
        for state_cls in self.states:
            if state_cls.value == value:
                state = state_cls
        return state

    def init_state(self):
        """
        Our default state initializer. This method can be overridden
        if the state is determined by more than just a field on the
        instance.

        If you override this method, make sure to call set_state() to
        set the state on the instance.
        """
        self.state = self.initial_state

        # Find the correct state field for the instance we need to manage state
        # for. We will assume a default state field name of `state` if this is
        # not provided
        self.state_field = self.extra_args.get('state_field', 'state')

        # Set up the current state based on the instance
        if self.instance:
            state_value = getattr(self.instance, self.state_field)
            if not state_value:
                state_value = self.initial_state.value

            # Now find and set correct state based on the instance
            self.state = self.get_state_by_value(state_value)

    def get_state_instance(self):
        """ Returns a single instance for the current state """
        return self.state(manager=self, **self.extra_args)

    def transition(self, action, *args, **kwargs):
        available_actions = [a[0] for a in self.state.get_actions()]
        if self.state and action not in available_actions:
            raise InvalidTransition('{}, is not a valid action for {}.'.format(
                action, self.state.value))
        state = getattr(self.get_state_instance(), action)(*args, **kwargs)
        self.state = state
        return self.state.value

    @classmethod
    def get_permissions(cls, model_name):
        """
        Returns the permissions for the different states and transitions
        as tuples, the same as what django's permission system expects.

        ``prefix`` is required so that we can specify on which model
        the permission applies.
        """
        perms = ()

        for state in cls.states:
            for perm in state.permissions:
                # permission codename format: "<state>_<action>_<modelname>"
                permission = (
                    '{}_{}_{}'.format(state.value, perm[0], model_name),
                    '[{}] {} {}'.format(
                        state.verbose_name,
                        perm[1],
                        model_name.capitalize(),
                    )
                )
                if permission not in perms:
                    perms += (permission,)

            # Now add the transition permissions
            for action, verbose in state.get_actions():
                perm = (
                    'can_{}_{}'.format(action, model_name),
                    'Can {} {}'.format(verbose, model_name.capitalize()),
                )
                if perm not in perms:  # Dont add it if it already exists
                    perms += (perm,)

        return perms
