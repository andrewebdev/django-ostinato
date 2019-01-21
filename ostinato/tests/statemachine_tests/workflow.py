from ostinato.statemachine import State, StateMachine


# States
class Private(State):
    verbose_name = 'Private'
    transitions = {'publish': 'public'}

    def publish(self, msg="Object made public"):
        if self.instance:
            self.instance.message = msg


class Public(State):
    verbose_name = 'Public'
    transitions = {'retract': 'private'}

    def retract(self):
        if self.instance:
            self.instance.message = 'Object made private'


class ErrorState(State):
    verbose_name = 'Error State'
    transitions = {'invalid_action': 'invalid'}  # Target state does not exist


class HangingState(State):
    verbose_name = 'Hanging State'
    transitions = {}


class TestStateMachine(StateMachine):
    state_map = {'private': Private, 'public': Public}
    initial_state = 'private'


class InvalidSM(StateMachine):
    state_map = {'private': Private, 'error': ErrorState, 'public': Public}
    initial_state = 'invalid'


class ErrorSM(InvalidSM):
    initial_state = 'private'


class HangingSM(InvalidSM):
    state_map = {'private': Private, 'hanging': HangingState, 'public': Public}
    initial_state = 'private'


# Create a Integer based Statemachine
class IntPrivate(State):
    verbose_name = 'Private'
    transitions = {'publish': 2}

    def publish(self):
        if self.instance:
            self.instance.message = 'Object made public'


class IntPublic(State):
    verbose_name = 'Public'
    transitions = {'retract': 1}

    def retract(self):
        if self.instance:
            self.instance.message = 'Object made private'


class TestIntegerStateMachine(StateMachine):
    state_map = {1: IntPrivate, 2: IntPublic}
    initial_state = 1


