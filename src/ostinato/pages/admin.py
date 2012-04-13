from django.contrib import admin
from django.contrib.admin.util import unquote

from mptt.admin import MPTTModelAdmin

from ostinato.pages.models import Page
from ostinato.pages.utils import get_zones_for


def inline_factory(zone_model):

    class ZoneInline(admin.StackedInline):
        model = zone_model
        exclude = ('zone_id',)
        extra = 0
        max_num = 1
        can_delete = False

    return ZoneInline


## Admin Models
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


    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        We need to dynamically create the inline models since it
        changes based on the template.
        """
        page = self.get_object(request, unquote(object_id))

        inlines = []

        if page is not None:
            for zone in get_zones_for(page):
                inlines.append(inline_factory(zone.__class__))

        self.inlines = inlines

        return super(PageAdmin, self).change_view(
            request, object_id, form_url='', extra_context=None)


admin.site.register(Page, PageAdmin)

