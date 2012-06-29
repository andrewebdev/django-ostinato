from django.contrib import admin

from ostinato.blog.workflow import BlogEntryWorkflow
from ostinato.statemachine.forms import sm_form_factory
from odemo.blog.models import Entry


class EntryAdmin(admin.ModelAdmin):
    form = sm_form_factory(BlogEntryWorkflow)

    list_display = ('title', 'slug', 'show_state', 'publish_date', 'allow_comments')
    list_filter = ('state', 'allow_comments')

    def show_state(self, obj):
        sm = BlogEntryWorkflow(instance=obj)
        return sm.state
    show_state.short_description = 'State'

admin.site.register(Entry, EntryAdmin)