from django.contrib import admin

from mptt.admin import MPTTModelAdmin
from ostinato.pages.models import Page


class PageAdmin(MPTTModelAdmin):
    list_display = ('title', 'slug', 'template', 'author', 'show_in_nav',
        'state', 'show_in_sitemap', 'created_date', 'modified_date',
        'publish_date')
    list_filter = ('template', 'author', 'show_in_nav', 'show_in_sitemap')
    search_fields = ('title', 'short_title', 'slug', 'author')
    date_hierarchy = 'publish_date'

    fieldsets = (
        (None, {
            'fields': (
                ('title', 'short_title', 'slug'),
                'template', 'redirect', 'parent',
                ('show_in_nav', 'show_in_sitemap'),
            ),
        }),

        ('Publication', {
            'fields': ('author', 'publish_date'),
        }),

    )
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Page, PageAdmin)

