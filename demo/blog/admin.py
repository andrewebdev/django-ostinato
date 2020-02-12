from django.contrib import admin

from ostinato.blog.workflow import BlogEntryWorkflow
from ostinato.statemachine.forms import sm_form_factory
from ckeditor.fields import RichTextFormField

from blog.models import Entry


class CustomEntryAdminForm(sm_form_factory(sm_class=BlogEntryWorkflow)):
    content = RichTextFormField()


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
