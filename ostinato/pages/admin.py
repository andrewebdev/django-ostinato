import os

from django.contrib import admin
from django.contrib.admin.util import unquote
from django import forms
from django.conf import settings

from mptt.admin import MPTTModelAdmin
from ostinato.statemachine.forms import sm_form_factory
from ostinato.pages.models import Page, PageWorkflow
from ostinato.pages.registry import page_content


def content_inline_factory(page):
    content_model = page.get_content_model()

    class PageContentInline(admin.StackedInline):
        model = content_model
        extra = 1
        max_num = 1
        can_delete = False
        fk_name = 'page'

        ## Check for a custom form and try to load it
        content_form = getattr(content_model.ContentOptions, 'form', None)
        if content_form:
            module_path, form_class = content_form.rsplit('.', 1)

            form = __import__(module_path, locals(), globals(),
                [form_class], -1).__dict__[form_class]

    return PageContentInline


## Admin Models
class PageAdminForm(sm_form_factory(sm_class=PageWorkflow)):  # <3 python

    template = forms.ChoiceField()
    
    def __init__(self, *args, **kwargs):
        super(PageAdminForm, self).__init__(*args, **kwargs)
        self.fields['template'].choices = page_content.get_template_choices()

    class Meta:
        model = Page


class PageAdmin(MPTTModelAdmin):
    save_on_top = True
    form = PageAdminForm

    list_display = ('title', 'reorder', 'slug', 'template_name', 'author',
        'page_state', 'show_in_nav', 'show_in_sitemap', 'publish_date')

    list_filter = ('author', 'show_in_nav', 'show_in_sitemap',
        'state')

    list_editable = ('show_in_nav', 'show_in_sitemap')

    search_fields = ('title', 'short_title', 'slug', 'author')
    date_hierarchy = 'publish_date'
    inlines = ()

    fieldsets = (
        (None, {
            'fields': (
                ('title', 'short_title'), 'slug',
                'template', 'redirect', 'parent',
                ('show_in_nav', 'show_in_sitemap'),
            ),
        }),

        ('Publication', {
            'fields': ('state', 'author', 'publish_date'),
        }),

    )
    prepopulated_fields = {'slug': ('title',)}

    if 'grappelli' in settings.INSTALLED_APPS:
        change_list_template = 'admin/ostinato_change_list_grappelli.html'
    else:
        change_list_template = 'admin/ostinato_change_list.html'

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
            static_prefix('pages/js/page_admin.js'),
        )


    def page_state(self, obj):
        sm = PageWorkflow(instance=obj)
        return sm.state
    page_state.short_description = 'State'


    def template_name(self, obj):
        return page_content.get_template_name(obj.template)
    template_name.short_description = 'Template'


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


    def add_view(self, request, form_url='', extra_context=None):
        # We need to clear the inlines. Django keeps it cached somewhere
        self.inlines = ()
        return super(PageAdmin, self).add_view(request, form_url, extra_context)


    def change_view(self, request, object_id, form_url='', extra_context=None):
        """
        We need to dynamically create the inline models since it
        changes based on the template.
        """
        self.inlines = ()

        if object_id:
            page = self.get_object(request, unquote(object_id))

            if page.template:
                self.inlines = (content_inline_factory(page),)

            content_model = page.get_content_model()
            if hasattr(content_model.ContentOptions, 'page_inlines'):
                for inline in content_model.ContentOptions.page_inlines:
                    self.inlines += (inline,)

        return super(PageAdmin, self).change_view(
            request, object_id, form_url, extra_context)


admin.site.register(Page, PageAdmin)

