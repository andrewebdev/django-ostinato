from django import forms


class StateMachineModelForm(forms.ModelForm):

    _sm_action = forms.ChoiceField(
        choices=[], label="Take Action", required=False)

    def __init__(self, *args, **kwargs):
        super(StateMachineModelForm, self).__init__(*args, **kwargs)

        # FIXME: This wont work if we dont have a instance saved yet.
        # Remove the try/except block once a proper solution has
        # been implemented

        try:
            actions = (('', '-- %s --' % self.instance.sm.state),)
            for action in self.instance.sm.get_actions():
                actions += ((action, self.instance.sm.get_action_display(action)),)

            self.fields['_sm_action'] = forms.ChoiceField(
                choices=actions, label="State/Actions", required=False)
        except:
            pass