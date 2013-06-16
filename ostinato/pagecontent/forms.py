from django import forms

from ostinato.pagecontent.models import ContactFormContent
from ostinato.utils import Emailer


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
