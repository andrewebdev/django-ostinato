from django import forms
from django.contrib.contenttypes.admin import GenericTabularInline
from ckeditor.fields import RichTextFormField

from website.models import (
    HomePage,
    GenericPage,
    CaseStudyPage,
    ContactPage,
    Image,
    Video
)
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


class ImageInline(GenericTabularInline):
    extra = 0
    model = Image


class VideoInline(GenericTabularInline):
    extra = 0
    model = Video


class _ContentForm(forms.ModelForm):
    content = RichTextFormField()


# Pages Admin Forms
class HomePageForm(_ContentForm):
    class Meta:
        model = HomePage
        fields = ('content', 'cache_page')


class GenericPageForm(_ContentForm):
    class Meta:
        model = GenericPage
        fields = ('content', 'cache_page')


class CaseStudyPageForm(_ContentForm):
    class Meta:
        model = CaseStudyPage
        fields = ('content', 'cache_page')


class ContactPageForm(_ContentForm):
    class Meta:
        model = ContactPage
        fields = ('content', 'recipients', 'email_subject', 'success_page')
