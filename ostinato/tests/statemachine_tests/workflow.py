from ostinato.statemachine import State, StateMachine, action


class Private(State):
    value = 'private'
    verbose_name = 'Private'

    @action('public')
    def publish(self, msg="Object made public"):
        self.manager.instance.message = msg


class Public(State):
    value = 'public'
    verbose_name = 'Public'

    @action('private')
    def retract(self):
        self.manager.instance.message = 'Object made private'


class TestStateMachine(StateMachine):
    states = (Private, Public)
    initial_state = Private


# Create a Integer based Statemachine
class IntPrivate(State):
    value = 1
    verbose_name = 'Private'

    @action(2)
    def publish(self):
        self.manager.instance.message = 'Object made public'


class IntPublic(State):
    value = 2
    verbose_name = 'Public'

    @action(1)
    def retract(self):
        self.manager.instance.message = 'Object made private'


class TestIntegerStateMachine(StateMachine):
    states = (IntPrivate, IntPublic)
    initial_state = IntPrivate
