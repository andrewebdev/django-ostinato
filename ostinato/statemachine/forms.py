from django import forms


class StateMachineModelForm(forms.ModelForm):

    _sm_action = forms.ChoiceField(
        choices=[], label="Take Action", required=False)


    def __init__(self, *args, **kwargs):
        super(StateMachineModelForm, self).__init__(*args, **kwargs)

        if self.instance.id:
            actions = (('', '-- %s --' % self.instance.sm.state),)
            for action in self.instance.sm.get_actions():
                actions += ((action, self.instance.sm.get_action_display(action)),)

            self.fields['_sm_action'] = forms.ChoiceField(
                choices=actions, label="State/Actions", required=False)


    def save(self, *args, **kwargs):
        """
        Override the save method so that we can take any required actions
        and move to the next state.
        """
        instance =  super(StateMachineModelForm, self).save(*args, **kwargs)
        
        action = self.cleaned_data['_sm_action']
        if action:
            self.instance.sm.take_action(action)

        return instance

