from django.test import TestCase
from django.test.client import RequestFactory

from ostinato.contentbrowser.core import get_browsers, BrowserNotFound
from ostinato.contentbrowser.views import BrowserView

from .views import SampleBrowser


# Now for the tests
class BrowserViewTestCase(TestCase):

    def test_get_items_raises_not_implemented(self):
        rf = RequestFactory()
        request = rf.get('/')
        view = BrowserView()

        with self.assertRaises(NotImplementedError):
            view.get_items(request)


class ContentBrowserRegistryTestCase(TestCase):

    def test_browser_not_found_exception(self):
        with self.assertRaises(BrowserNotFound):
            get_browsers('invalid')

    def test_get_browser_returns_all(self):
        browsers = get_browsers()
        self.assertEqual([SampleBrowser], browsers)

    def test_get_browser_returns_single_browser(self):
        browser = get_browsers('samples')
        self.assertEqual(SampleBrowser, browser)
