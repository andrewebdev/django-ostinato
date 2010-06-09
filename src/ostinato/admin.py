from django.contrib import admin
from django.contrib.contenttypes import generic

from ostinato.models import ContentItem

## Admin Actions
def action_publish(modeladmin, request, queryset):
    for item in queryset:
        item.action_publish()
action_publish.short_description = "Mark selected items as Published"

def action_draft(modeladmin, request, queryset):
    for item in queryset:
        item.action_draft()
action_draft.short_description = "Mark selected items as Draft"

def action_review(modeladmin, request, queryset):
    for item in queryset:
        item.action_review()
action_review.short_description = "Mark selected items for Review"

def action_hidden(modeladmin, request, queryset):
    for item in queryset:
        item.action_hide()
action_hidden.short_description = "Mark selected items as Hidden"

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
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'short_title', 'status',
                    'allow_comments', 'show_in_nav',
                    'created_date', 'modified_date', 'publish_date'
    ]
    list_filter = ['status', 'allow_comments', 'show_in_nav', 'publish_date']
    date_hierarchy = 'created_date'
    search_fields = ['title', 'short_title', 'description', 'location']
    actions = [action_publish, action_draft, action_review, action_hidden,
               action_show_in_nav, action_dont_show_in_nav,
               action_allow_comments, action_disallow_comments]
    fieldsets = (
        (None, {
            'fields': ('title', 'short_title', 'description'),
        }),
        ('Content Properties', {
            'fields': ('parent', 'status', 'allow_comments', 'show_in_nav',
                       'tags', 'location')
        }),
        ('Authoring and Publication', {
            'fields': ('publish_date', 'authors', 'contributors')
        }),
    )

## Admin registrations
admin.site.register(ContentItem, ContentItemAdmin)
