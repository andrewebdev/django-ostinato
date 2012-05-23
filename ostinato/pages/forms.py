from django import forms

from ostinato.pages.models import Page


class MovePageForm(forms.Form):

    node = forms.IntegerField()
    target = forms.IntegerField()
    position = forms.CharField()

    def save(self, *args, **kwargs):
        page_id = self.cleaned_data['node']
        target_id = self.cleaned_data['target']
        position = self.cleaned_data['position']

        page = Page.objects.get(id=page_id)
        target= Page.objects.get(id=target_id)
        page.move_to(target, position)
