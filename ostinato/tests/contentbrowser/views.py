from ostinato.contentbrowser.views import BrowserView


class SampleBrowser(BrowserView):
    title = "Sample Browser"
    description = ""
    browser_id = "samples"
    template_name = "browsers/sample.html"

    def get_items(self, request):
        return [{
            'title': 'Sample Item',
            'text': 'Some sample text for Sample Item',
        }, {
            'title': 'Second Sample',
            'text': 'Sample content for the second item',
        }]
