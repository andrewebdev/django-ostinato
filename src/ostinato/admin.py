from django.contrib import admin
from django.contrib.contenttypes import generic
from django import forms

from ostinato.models import ContentItem, BasicPage

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
def statemachine_form(for_model=None):
    """
    Factory function to create a special case form that will render
    an extra _sm_actions choice field, showing only the available actions
    for the current state.
    """
    class _StateMachineBaseModelForm(forms.ModelForm):
        _sm_action = forms.ChoiceField(choices=[], label="Take Action",
                                       required=False)

        class Meta:
            model = for_model

        def __init__(self, *args, **kwargs):
            super(_StateMachineBaseModelForm, self).__init__(*args, **kwargs)
            actions = (('', '-- %s --' % self.instance.sm_state),)
            for action in self.instance.sm_state_actions():
                actions += ((action, action),)
            self.fields['_sm_action'] = forms.ChoiceField(
                choices=actions, label="Take Action", required=False)

        def save(self, *args, **kwargs):
            """
            Override the save method so that we can take any required actions
            and move to the next state.
            """
            action = self.cleaned_data['_sm_action']
            if action: self.instance.sm_take_action(action)
            return super(_StateMachineBaseModelForm, self).save(*args, **kwargs)

    if for_model: return _StateMachineBaseModelForm
    else: return None

class ContentItemAdmin(admin.ModelAdmin):
    form = statemachine_form(for_model=ContentItem)

    list_display = ['title', 'slug', 'short_title', 'parent', 'template',
                    'order', 'sm_state_admin',
                    'allow_comments', 'show_in_nav',
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
            'fields': ('parent', 'allow_comments', 'show_in_nav', 'tags')
        }),
        ('Authoring and Publication', {
            'fields': ('publish_date', 'authors', 'contributors', '_sm_action')
        }),
    )

## Admin registrations
admin.site.register(ContentItem, ContentItemAdmin)
admin.site.register(BasicPage)
