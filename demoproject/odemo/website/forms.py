from django import forms
from tinymce.widgets import TinyMCE
from website.models import RichContent


# Pages Admin Forms
class RichContentForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = RichContent
