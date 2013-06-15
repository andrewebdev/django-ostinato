from django import forms

from ostinato.pages.models import Page
from ostinato.pages.registry import page_templates


class MovePageForm(forms.Form):

    node = forms.IntegerField()
    target = forms.IntegerField()
    position = forms.CharField()

    def clear_page_cache(self):
        Page.objects.clear_url_cache()
        Page.objects.clear_navbar_cache()
        Page.objects.clear_breadcrumbs_cache()

    def save(self, *args, **kwargs):
        page_id = self.cleaned_data['node']
        target_id = self.cleaned_data['target']
        position = self.cleaned_data['position']

        page = Page.objects.get(id=page_id)
        target= Page.objects.get(id=target_id)

        # IMPORTANT: Clear the url, navbar and breadcrumbs cache
        self.clear_page_cache()

        # Now move the page
        page.move_to(target, position)


class DuplicatePageForm(MovePageForm):

    def save(self, *args, **kwargs):
        page_id = self.cleaned_data['node']
        target_id = self.cleaned_data['target']
        position = self.cleaned_data['position']

        page = Page.objects.get(id=page_id)
        target = Page.objects.get(id=target_id)

        # IMPORTANT: Clear the url, navbar and breadcrumbs cache
        self.clear_page_cache()

        # Create and save the duplicate page
        page.pk = None
        page.slug += '-copy'
        new_page = Page.objects.insert_node(page, target,
                                            position=position, save=True)
        # Also duplicate the page content
        template = page_templates.get_template(new_page.template)

        for content_path in template.page_content:
            # import the content model
            try:
                module_path, inline_class = content_path.rsplit('.', 1)
                model = __import__(
                    module_path, locals(), globals(),
                    [inline_class], -1).__dict__[inline_class]

            except KeyError:
                raise Exception(
                    '"%s" could not be imported from, '
                    '"%s". Please check the import path for the page '
                    'inlines' % (inline_class, module_path))

            except AttributeError:
                raise Exception(
                    'Incorrect import path for page '
                    'content inlines. Expected a string containing the'
                    ' full import path.')

            page_content = model.objects.filter(page__id=page_id)

            for content in page_content:
                content.pk = None
                content.page = new_page
                content.save()
