from django import forms


def sm_form_factory(sm_class, state_field='state'):
    """
    A factory function to create our StateMachineModelForm and return it
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

        def save(self, *args, **kwargs):
            """
            Override the save method so that we can perform statemachine
            actions.
            """
            # We need a new statemachine with the stored_sate
            sm = sm_class(instance=self.instance, state_field=state_field,
                state=self.old_state)

            # Try to get a valid action from the current state_field
            action = getattr(self.instance, state_field)
            if action in sm.actions:
                sm.take_action(action)

            # Ok, we can now save our form as normal
            return super(StateMachineModelForm, self).save(*args, **kwargs)

    return StateMachineModelForm

