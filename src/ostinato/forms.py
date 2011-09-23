from django import forms
from ostinato.models import ContentItem


class ContentItemForm(forms.ModelForm):
	class Meta:
		model = ContentItem
		exclude = ('order', 'content_type', 'object_id', '_sm_state')

	def __init__(self, *args, **kwargs):
            super(ContentItemForm, self).__init__(*args, **kwargs)
            actions = (('', '-- %s --' % self.instance.sm_state),)
            for action in self.instance.sm_state_actions():
                actions += ((action, action),)
            self.fields['_sm_action'] = forms.ChoiceField(
                choices=actions, label="State", required=False)

        def save(self, *args, **kwargs):
            """
            Override the save method so that we can take any required actions
            and move to the next state.
            """
            action = self.cleaned_data['_sm_action']
            if action:
	            self.instance.sm_take_action(action)
            return super(ContentItemForm, self).save(*args, **kwargs)