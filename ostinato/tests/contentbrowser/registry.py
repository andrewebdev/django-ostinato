from ostinato.contentbrowser.registry import ContentBrowser, cbregistry
from .models import DemoModel


@cbregistry.register
class DemoModelItems(ContentBrowser):
    # content_type = 'contentbrowser.demomodel'
    title = 'Demo Model'

    def get_items(self, request):
        return DemoModel.objects.all()
