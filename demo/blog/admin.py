from django.contrib import admin
from django import forms

from ostinato.blog.workflow import BlogEntryWorkflow
from ostinato.statemachine.forms import sm_form_factory
from ostinato.contentbrowser.widgets import CBWidgetMixin

from blog.models import Entry


class EditorWidget(CBWidgetMixin):
    pass


class CustomEntryAdminForm(sm_form_factory(sm_class=BlogEntryWorkflow)):
    content = forms.CharField(widget=EditorWidget())


class EntryAdmin(admin.ModelAdmin):
    form = CustomEntryAdminForm

    list_display = (
        'title',
        'slug',
        'author',
        'entry_state',
        'created_date',
        'publish_date'
    )

    list_filter = ('state', 'author')

    def entry_state(self, obj):
        sm = BlogEntryWorkflow(instance=obj)
        return sm.state.verbose_name
    entry_state.short_description = "State"


admin.site.register(Entry, EntryAdmin)
