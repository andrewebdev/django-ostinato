import new
from django import forms
from ostinato.statemachine import InvalidTransition


def sm_form_factory(sm_class, state_field='state'):
    """
    A factory to create a custom StateMachineModelForm class
    """
    class StateMachineModelForm(forms.ModelForm):

        def __init__(self, *args, **kwargs):
            super(StateMachineModelForm, self).__init__(*args, **kwargs)

            sm = sm_class(instance=self.instance, state_field=state_field)
            self.old_state = sm._state
            actions = ((sm._state, '-- %s --' % sm.state),)

            for action in sm.actions:
                actions += ((action, action),)

            self.fields[state_field] = forms.ChoiceField(
                choices=actions, label="State/Actions", required=False)

            # We need a custom clean method for the state_field. Since
            # django expects this method to be called ``clean_<field_name>``
            # we will have to dynamically generate it here
            def clean_action(self):
                """
                make sure that the selected action does not pass through to
                the actual form cleaned_data, since it can cause validation
                issues on the field.
                """
                self._sm_action = self.cleaned_data[state_field]
                try:
                    return sm.action_result(self._sm_action)
                except InvalidTransition:
                    return self.old_state
            setattr(self, 'clean_%s' % state_field,
                    new.instancemethod(clean_action, self, None))

        def take_action(self):
            """
            This is where we pass the form values to the StateMachine
            to do it's thing.
            """
            sm = sm_class(instance=self.instance, state_field=state_field,
                          state=self.old_state)

            # The ``clean_<state_field>`` method stored the action in self
            if self._sm_action in sm.actions:
                sm.take_action(self._sm_action)

        def save(self, *args, **kwargs):
            """
            Override the save method so that we can perform statemachine
            actions.

            For most simple cases this is all that is required. If however
            you want to do more advanced processing based on the state/action,
            then you should override the save method and call ``take_action()``
            when you are ready.
            """
            self.take_action()
            return super(StateMachineModelForm, self).save(*args, **kwargs)

    return StateMachineModelForm

