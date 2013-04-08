from django import forms

from tinymce.widgets import TinyMCE
from website.models import HomePage, GenericPage, CaseStudyPage, ContactPage


class HomePageForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE())
    
    class Meta:
        model = HomePage


class GenericPageForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = GenericPage


class CasteStudyPageForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = CaseStudyPage


class ContactPageForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = ContactPage