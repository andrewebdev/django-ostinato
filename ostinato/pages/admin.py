from django.contrib import admin
from django.contrib.admin.util import unquote
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from django import forms
from django.conf import settings

from mptt.admin import MPTTModelAdmin
from ostinato.statemachine.forms import sm_form_factory
from ostinato.pages.models import Page
from ostinato.pages.workflow import get_workflow
from ostinato.pages.registry import page_content


# Some helpers to get the icons
def staticurl(p):
    staticurl = settings.STATIC_URL
    if staticurl[-1] == '/':
        return '%s%s' % (staticurl, p)
    else:
        return '%s/%s' % (staticurl, p)


def geticon(action):
    return '<img src="%s" />' % staticurl('pages/img/%s.png' % action)


def content_inline_factory(page):
    content_model = page.get_content_model()

    class PageContentInline(admin.StackedInline):
        model = content_model
        extra = 1
        max_num = 1
        can_delete = False
        fk_name = 'page'
        classes = ('grp-collapse grp-open',)
        inline_classes = ('grp-collapse grp-open',)

        ## Check for a custom form and try to load it
        content_form = getattr(content_model.ContentOptions, 'form', None)
        if content_form:
            module_path, form_class = content_form.rsplit('.', 1)

            form = __import__(
                module_path, locals(), globals(), [form_class], -1
            ).__dict__[form_class]

    return PageContentInline


## Admin Models
class PageAdminForm(sm_form_factory(sm_class=get_workflow())):  # <3 python

    template = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(PageAdminForm, self).__init__(*args, **kwargs)
        self.fields['template'].choices = page_content.get_template_choices()

    class Meta:
        model = Page


class PageAdmin(MPTTModelAdmin):
    save_on_top = True
    form = PageAdminForm

    list_display = (
        'tree_node', 'get_title', 'page_actions', 'slug',
        'template_name', 'page_state', 'show_in_nav', 'show_in_sitemap')
    list_display_links = ('get_title',)
    list_filter = ('show_in_nav', 'show_in_sitemap', 'state')

    search_fields = ('title', 'short_title', 'slug',)
    date_hierarchy = 'publish_date'
    inlines = ()

    fieldsets = (
        (None, {
            'fields': (
                ('title', 'short_title'),
                'slug', 'template', 'redirect', 'parent',
                ('show_in_nav', 'show_in_sitemap'),
            ),
        }),

        ('Publication', {
            'fields': ('state', 'publish_date'),
        }),

    )
    prepopulated_fields = {'slug': ('title',)}

    if 'grappelli' in settings.INSTALLED_APPS:
        change_list_template = 'admin/pages_change_list_grappelli.html'
    else:
        change_list_template = 'admin/pages_change_list.html'

    class Media:

        css = {
            'all': (
                'pages/css/pages_admin.css',
            ),
        }

        js = (
            'pages/js/page_admin.js',
        )

    def tree_node(self, obj):
        """
        A custom title for the list display that will be indented based on
        the level of the node, as well as display a expand/collapse icon
        if the node has any children.

        This node will also have some information for the row, like the
        level etc.
        """
        content = '<span id="tid_%s_%s_%s_%s" class="tree_node closed">' % (
            obj.tree_id, obj.level, obj.lft, obj.rght)
        if obj.get_descendant_count() > 0:
            content += '<a class="toggle_children" href="#">%s</a>' % geticon('tree_closed')
        content += '</span>'
        return content
    tree_node.short_description = ''
    tree_node.allow_tags = True

    def get_title(self, obj):
        PAGES_SITE_TREEID = getattr(settings, 'OSTINATO_PAGES_SITE_TREEID', None)
        PAGES_INDENT = getattr(settings, 'OSTINATO_PAGES_ADMIN_INDENT', 4 * '&nbsp;')

        title = obj.get_short_title()

        if PAGES_SITE_TREEID:
            if obj.level == 0:
                try:
                    tree_site = Site.objects.get(id=obj.tree_id)
                except:
                    return '%s (No Site)' % title
                return '%s (%s)' % (title, tree_site.name)

        return '%s%s' % (PAGES_INDENT * obj.level, title)
    get_title.short_description = _("Title")
    get_title.allow_tags = True

    def page_state(self, obj):
        sm = get_workflow()(instance=obj)
        return sm.state
    page_state.short_description = _("State")

    def template_name(self, obj):
        return page_content.get_template_name(obj.template)
    template_name.short_description = _("Template")

    def page_actions(self, obj):
        """ A List view item that shows the movement actions """
        return render_to_string('admin/pages_actions.html', {'obj': obj})
    page_actions.short_description = _("Actions")
    page_actions.allow_tags = True

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
            if hasattr(content_model.ContentOptions, 'admin_inlines'):
                for inline_def in content_model.ContentOptions.admin_inlines:
                    through = None

                    if isinstance(inline_def, (str, unicode)):
                        inline_str = inline_def
                    else:
                        inline_str, through = inline_def

                    try:
                        module_path, inline_class = inline_str.rsplit('.', 1)
                        inline = __import__(module_path, locals(), globals(),
                            [inline_class], -1).__dict__[inline_class]

                    except KeyError:
                        raise Exception('"%s" could not be imported from, '\
                            '"%s". Please check the import path for the page '\
                            'inlines' % (inline_class, module_path))

                    except AttributeError:
                        raise Exception('Incorrect import path for page '\
                            'content inlines. Expected a string containing the'\
                            ' full import path.')

                    self.inlines += (inline,)

        return super(PageAdmin, self).change_view(
            request, object_id, form_url, extra_context)


admin.site.register(Page, PageAdmin)
