from django import forms

from ckeditor.widgets import CKEditorWidget
from models import ListPage


class CustomForm(forms.ModelForm):
    """
    A custom form that will take the content field and replace
    it with a richtextfield (provided by django-ckeditor in this case)
    """
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = ListPage


