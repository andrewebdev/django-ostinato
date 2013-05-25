from django import forms

from ostinato.pages.models import Page


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
        try:
            page_content = page.get_content_model().objects.get(page=page)
        except:
            page_content = None

        target = Page.objects.get(id=target_id)

        # IMPORTANT: Clear the url, navbar and breadcrumbs cache
        self.clear_page_cache()

        # Create and save the duplicate page
        page.pk = None
        page.slug += '-copy'
        new_page = Page.objects.insert_node(page, target,
                                            position=position, save=True)
        # Also duplicate the page content
        if page_content:
            page_content.pk = None
            page_content.page = new_page
            page_content.save()
