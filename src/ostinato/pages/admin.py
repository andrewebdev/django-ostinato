import os

from django.contrib import admin
from django.contrib.admin.util import unquote
from django.conf import settings

from mptt.admin import MPTTModelAdmin

from ostinato.statemachine.forms import StateMachineModelForm
from ostinato.pages.models import Page, DefaultStateMachine
from ostinato.pages.utils import get_zones_for


def inline_factory(zone_instance, page):

    class ZoneInline(admin.StackedInline):
        model = zone_instance.__class__
        exclude = ('zone_id',)
        extra = 0
        max_num = 1
        can_delete = False

        def queryset(self, request):
            qs = super(ZoneInline, self).queryset(request)
            return qs.filter(zone_id=zone_instance.zone_id, page=page).distinct()

    return ZoneInline


class PageAdminForm(StateMachineModelForm):

    class Meta:
        model = Page


## Admin Models
class PageAdmin(MPTTModelAdmin):
    form = PageAdminForm
    save_on_top = True

    list_display = ('title', 'reorder', 'slug', 'template',
        'author', 'state', 'show_in_nav', 'show_in_sitemap',
        'publish_date')

    list_filter = ('template', 'author', 'show_in_nav', 'show_in_sitemap',
        '_sm__state')

    search_fields = ('title', 'short_title', 'slug', 'author')
    date_hierarchy = 'publish_date'

    fieldsets = (
        (None, {
            'fields': (
                ('title', 'short_title'), 'slug',
                'template', 'redirect', 'parent',
                ('show_in_nav', 'show_in_sitemap'),
            ),
        }),

        ('Publication', {
            'fields': ('author', 'publish_date', '_sm_action'),
        }),

    )
    prepopulated_fields = {'slug': ('title',)}

    class Media:
        static_prefix = lambda p: os.path.join(settings.STATIC_URL, '%s' % p)

        css = {
            'all': (
                static_prefix('ostinato/css/smoothness/jquery-ui-1.8.18.custom.css'),
                static_prefix('pages/css/pages_admin.css'),
            ),
        }

        js = (
            static_prefix('ostinato/js/jquery-1.7.1.min.js'),
            static_prefix('ostinato/js/jquery-ui-1.8.18.custom.min.js'),
            static_prefix('ostinato/jstree/jquery.jstree.js'),
            static_prefix('pages/js/page_admin.js'),
        )

    def state(self, obj):
        """ Just a helper for the admin """
        return obj.sm.state

    def reorder(self, obj):
        """ A List view item that shows the movement actions """
        return '''<span id="_page_%s">
        <a class="ostinato_page_move" href="#">Move</a>
        <a class="ostinato_move_action _left_of" href="#">Before</a>
        <a class="ostinato_move_action _right_of" href="#">After</a>
        <a class="ostinato_move_action _child_of" href="#">Inside</a>
        <a class="ostinato_cancel_move" href="#">Cancel</a>
        </span>
        ''' % (obj.id)
    reorder.short_description = 'Re-order'
    reorder.allow_tags = True


    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        We need to dynamically create the inline models since it
        changes based on the template.
        """
        page = self.get_object(request, unquote(object_id))

        inlines = []

        if page is not None:
            for zone in get_zones_for(page):
                inlines.append(inline_factory(zone, page))

        # Note: doing self.inlines.append(inlines) will cause a bug where 
        # the same zones will show multiple times.
        self.inlines = inlines

        return super(PageAdmin, self).change_view(
            request, object_id, form_url='', extra_context=None)


admin.site.register(Page, PageAdmin)

