from django.contrib import admin
from django import forms

from blog.models import Entry
from ostinato.blog.workflow import BlogEntryWorkflow
from ostinato.statemachine.forms import sm_form_factory


class EntryAdmin(admin.ModelAdmin):
    form = sm_form_factory(sm_class=BlogEntryWorkflow)

    list_display = ('title', 'slug', 'author', 'entry_state', 'created_date',
        'publish_date')
    list_filter = ('state', 'author')

    def entry_state(self, obj):
        sm = BlogEntryWorkflow(instance=obj)
        return sm.state
    entry_state.short_description = "State"


admin.site.register(Entry, EntryAdmin)
