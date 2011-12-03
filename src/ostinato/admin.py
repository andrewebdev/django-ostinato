from datetime import datetime

from django.contrib import admin
from django.contrib.contenttypes import generic
from django import forms

from ostinato.models import ContentItem, BasicPage
from ostinato.statemachine.forms import StateMachineModelForm


## Admin Actions
def action_allow_comments(modeladmin, request, queryset):
    queryset.update(allow_comments=True)
action_allow_comments.short_description = "Comments - Allow comments on items"

def action_disallow_comments(modeladmin, request, queryset):
    queryset.update(allow_comments=False)
action_disallow_comments.short_description = "Comments - Disallow comments on items"

def action_show_in_nav(modeladmin, request, queryset):
    queryset.update(show_in_nav=True)
action_show_in_nav.short_description = "Navigation - Show Items in Nav"

def action_dont_show_in_nav(modeladmin, request, queryset):
    queryset.update(show_in_nav=False)
action_dont_show_in_nav.short_description = "Navigation - Dont show in Nav"


## Inline Classes
class ContentItemInline(generic.GenericStackedInline):
    model = ContentItem
    extra = 0


## ModelAdmin Classes
class ContentItemAdminForm(StateMachineModelForm):

    class Meta:
        model = ContentItem

    def save(self, *args, **kwargs):
        """
        Override the save method so that we can take any required actions
        and move to the next state.
        """
        kwargs['commit'] = False
        cms_item = super(ContentItemAdminForm, self).save(*args, **kwargs)
        action = self.cleaned_data['_sm_action']

        if action == 'make_public' and not cms_item.publish_date:
            cms_item.publish_date = datetime.now()

        elif kwargs['action'] == 'archive':
            cms_item.allow_comments = False

        if action:
            cms_item.sm.take_action(action)

        cms_item.save()

        return cms_item


class ContentItemAdmin(admin.ModelAdmin):
    form = ContentItemAdminForm

    list_display = ['title', 'slug', 'short_title', 'parent', 'template',
                    'order', 'state', 'allow_comments', 'show_in_nav',
                    'created_date', 'modified_date', 'publish_date']
    list_filter = ['allow_comments', 'show_in_nav', 'publish_date']
    date_hierarchy = 'created_date'
    search_fields = ['title', 'short_title', 'description']
    actions = [action_show_in_nav, action_dont_show_in_nav,
               action_allow_comments, action_disallow_comments]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'short_title', 'description',
                       'template', 'order'),
        }),
        ('Content Properties', {
            'fields': ('parent', 'location', 'allow_comments',
                       'show_in_nav', 'tags')
        }),
        ('Authoring and Publication', {
            'fields': ('publish_date', 'authors', 'contributors', '_sm_action')
        }),
    )


## Admin registrations
admin.site.register(ContentItem, ContentItemAdmin)
admin.site.register(BasicPage)
