import types
from django import forms
from ostinato.statemachine import InvalidTransition


def sm_form_factory(sm_class, state_field='state', **sm_kwargs):
    """
    A factory to create a custom StateMachineModelForm class
    """
    class StateMachineModelForm(forms.ModelForm):
        def __init__(self, *args, **kwargs):
            super(StateMachineModelForm, self).__init__(*args, **kwargs)

            self.sm = sm_class(
                instance=self.instance,
                state_field=state_field,
                **sm_kwargs)
            self.initial_state = self.sm.state.value

            self.fields[state_field] = forms.ChoiceField(
                choices=self.get_state_field_choices(),
                label="State/Actions",
                required=False)

            # We need a custom clean method for the state_field. Since
            # django expects this method to be called ``clean_<field_name>``
            # we will have to dynamically generate it here
            def clean_action(self):
                """
                make sure that the selected action does not pass through to
                the actual form cleaned_data, since it can cause validation
                issues on the field.
                """
                # Use a temporary statemachine without instance to "simulate"
                # a transition without modifying the instance.
                tempsm = sm_class(**sm_kwargs)
                tempsm.state = self.sm.state

                action = self.cleaned_data[state_field]

                if action == self.sm.state.value:
                    # In this case the state field didn't change changed.
                    return action

                try:
                    self._action_taken = action
                    return tempsm.transition(action)
                except InvalidTransition:
                    raise forms.ValidationError(
                        'Invalid transition, {}, for state, {}'.format(
                            action,
                            self.sm.state.verbose_name,
                        )
                    )

            # Now dynamically add the clean_<state_field> method to the form
            setattr(
                self,
                'clean_{}'.format(state_field),
                types.MethodType(clean_action, self))

        def get_state_field_choices(self):
            choices = [(
                self.sm.state.value,
                '-- {} --'.format(self.sm.state.verbose_name)
            )]
            choices += (
                (action, verbose)
                for action, verbose in self.sm.state.get_actions()
            )
            return choices

        def save(self, *args, **kwargs):
            """
            Override the save method so that we can perform statemachine
            actions.

            For most simple cases this is all that is required. If however
            you want to do more advanced processing based on the state/action,
            then you should override the save method and call ``transition()``
            when you are ready.
            """
            action = getattr(self, '_action_taken', None)
            if action:
                self.sm.transition(action)
            return super().save(*args, **kwargs)

    return StateMachineModelForm
