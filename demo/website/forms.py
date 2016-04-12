from django import forms

from tinymce.widgets import TinyMCE
from website.models import HomePage, GenericPage, CaseStudyPage, ContactPage
from website.utils import Emailer


class ContactForm(forms.Form):
    name = forms.CharField(max_length=150)
    website = forms.URLField(required=False)
    email = forms.EmailField()
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea())

    def save(self, recipients):
        context = self.cleaned_data.copy()
        email = Emailer(
            recipients=recipients,
            from_address="no-reply@tehnode.co.uk",
            subject_template="contact/subject.txt",
            body_template="contact/body.txt",
            context=context
        )
        email.send()


# Pages Admin Forms
class HomePageForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = HomePage
        fields = ('content',)


class GenericPageForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = GenericPage
        fields = ('content',)


class CasteStudyPageForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = CaseStudyPage
        fields = ('content',)


class ContactPageForm(forms.ModelForm):
    content = forms.CharField(widget=TinyMCE())

    class Meta:
        model = ContactPage
        fields = ('content',)

