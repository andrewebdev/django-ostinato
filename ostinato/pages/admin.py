from importlib import import_module

from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django import forms
from django.conf import settings

from mptt.admin import MPTTModelAdmin
from ostinato.statemachine.forms import sm_form_factory
from ostinato.pages.models import Page, get_content_model
from ostinato.pages.workflow import get_workflow


def content_inline_factory(page):
    content_model = get_content_model(page.template)

    class PageContentInline(admin.StackedInline):
        model = content_model
        extra = 1
        max_num = 1
        can_delete = False
        fk_name = 'page'
        # TODO: Can remove this because we will drop grappelli support
        classes = ('grp-collapse grp-open',)
        inline_classes = ('grp-collapse grp-open',)

        # Check for a custom form and try to load it
        content_form = getattr(content_model.ContentOptions, 'form', None)
        if content_form:
            module_path, form_class = content_form.rsplit('.', 1)
            form = getattr(import_module(module_path), form_class)

    return PageContentInline


# Admin Models
class PageAdminForm(sm_form_factory(sm_class=get_workflow())):  # <3 python

    template = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(PageAdminForm, self).__init__(*args, **kwargs)

        templates = getattr(settings, 'OSTINATO_PAGES')['templates']
        self.fields['template'].choices = templates

        self.fields['parent'].widget.can_add_related = False
        self.fields['parent'].widget.can_change_related = False
        if self.instance:
            self.fields['parent'].queryset = Page.objects.exclude(
                    id=self.instance.id)

    class Meta:
        model = Page
        fields = (
            'title',
            'short_title',
            'slug',
            'template',
            'redirect',
            'parent',
            'show_in_sitemap',
            'state',
            'publish_date',
        )


class PageAdmin(MPTTModelAdmin):
    save_on_top = True
    form = PageAdminForm

    list_display = (
        'get_title',
        'template_name',
        'page_state',
        'show_in_sitemap',
    )

    list_filter = (
        'state',
        'show_in_sitemap',
    )

    search_fields = ('title', 'short_title', 'slug')

    list_display_links = ('get_title',)
    inlines = ()

    fieldsets = (
        (None, {
            'fields': (
                ('title', 'short_title'),
                'slug',
                'template',
                'redirect',
                'parent',
                'show_in_sitemap',
            ),
        }),

        ('Publication', {
            'fields': ('state', 'publish_date'),
        }),

    )
    prepopulated_fields = {'slug': ('title',)}
    change_list_template = 'admin/pages_change_list.html'

    class Media:
        js = (
            'pages/js/page_admin.js',
        )

    def get_title(self, obj):
        """
        Provide the node and tree id's so that we can use this information
        in the javascript functions to manipulate page positions etc.
        """
        title = obj.get_short_title()
        if len(title) > 20:
            title = '{0} ...'.format(title[:20])

        return mark_safe('''
            <ost-page-node
                editUrl="{edit_url}"
                nodeId="{id}"
                treeId="{tree_id}"
                level="{level}"
                left="{left}"
                right="{right}">
                <span slot="title">{title}</span>
            </ost-page-node>'''.format(
                edit_url=reverse('admin:ostinato_pages_page_change', args=(obj.id,)),
                id=obj.id,
                tree_id=obj.tree_id,
                level=obj.level,
                left=obj.lft,
                right=obj.rght,
                title=title
            ))
    get_title.short_description = _("Title")

    def page_state(self, obj):
        sm = get_workflow()(instance=obj)
        return sm.state
    page_state.short_description = _("State")

    def template_name(self, obj):
        templates = getattr(settings, 'OSTINATO_PAGES')['templates']
        for t in templates:
            if t[0] == obj.template:
                return t[1]
    template_name.short_description = _("Template")

    def get_ordering(self, obj):
        return None

    def add_view(self, request, form_url='', extra_context=None):
        # We need to clear the inlines. Django keeps it cached somewhere
        self.inlines = ()
        return super(PageAdmin, self).add_view(
            request,
            form_url,
            extra_context
        )

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

            content_model = get_content_model(page.template)
            if hasattr(content_model.ContentOptions, 'admin_inlines'):
                for inline_def in content_model.ContentOptions.admin_inlines:
                    through = None

                    if isinstance(inline_def, (bytes, str)):
                        inline_str = inline_def
                    else:
                        inline_str, through = inline_def
                    try:
                        module_path, inline_class = inline_str.rsplit('.', 1)
                        inline = getattr(import_module(module_path),
                                         inline_class)
                    except KeyError:
                        raise Exception(
                            '"%s" could not be imported from, '
                            '"%s". Please check the import path for the page '
                            'inlines' % (inline_class, module_path))
                    except AttributeError:
                        raise Exception(
                            'Incorrect import path for page '
                            'content inlines. Expected a string containing '
                            'the full import path.')

                    self.inlines += (inline,)

        return super(PageAdmin, self).change_view(
            request, object_id, form_url, extra_context)


admin.site.register(Page, PageAdmin)
