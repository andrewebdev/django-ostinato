from django import forms

from ostinato.pages.models import Page, get_content_model


class MovePageForm(forms.Form):

    node = forms.IntegerField()
    target = forms.IntegerField()
    position = forms.CharField()

    def clear_page_cache(self):
        Page.objects.clear_url_cache()
        Page.objects.clear_breadcrumbs_cache()

    def save(self, *args, **kwargs):
        page_id = self.cleaned_data['node']
        target_id = self.cleaned_data['target']
        position = self.cleaned_data['position']

        page = Page.objects.get(id=page_id)
        target= Page.objects.get(id=target_id)

        # IMPORTANT: Clear the url and breadcrumbs cache
        self.clear_page_cache()

        # Now move the page
        page.move_to(target, position)


class DuplicatePageForm(MovePageForm):

    def save(self, *args, **kwargs):
        page_id = self.cleaned_data['node']
        target_id = self.cleaned_data['target']
        position = self.cleaned_data['position']

        page = Page.objects.get(id=page_id)

        # Get the page content if it exists
        try:
            content_model = get_content_model(page.template)
            page_content = content_model.objects.get(page=page)
        except content_model.DoesNotExist:
            page_content = None

        target = Page.objects.get(id=target_id)

        # IMPORTANT: Clear the url and breadcrumbs cache
        self.clear_page_cache()

        # Create and save the duplicate page
        page.pk = None
        page.slug += '-copy'
        new_page = Page.objects.insert_node(
            page,
            target,
            position=position,
            save=True
        )

        # Also duplicate the page content, if it exists
        if page_content:
            page_content.pk = None
            page_content.page = new_page
            page_content.save()

        return new_page
