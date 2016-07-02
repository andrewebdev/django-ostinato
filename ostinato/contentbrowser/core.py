from . import CONTENTBROWSER


__all__ = ['BrowserNotFound', 'get_browsers']


class BrowserNotFound(Exception):
    def __init__(self, browser_id):
        self.browser_id = browser_id

    def __str__(self):
        return "Content Browser '%s' not found" % self.browser_id


def get_browsers(browser_id=None):
    """
    Returns a list of browsers, or just a single one if browser_id is supplied
    """
    browsers = []

    for import_string in CONTENTBROWSER['browsers']:
        module_path, browser_class = import_string.rsplit('.', 1)
        browser = __import__(module_path, locals(), globals(),
                             [browser_class], -1).__dict__[browser_class]

        if browser_id is not None and browser.browser_id == browser_id:
            return browser

        browsers.append(browser)

    if browser_id is not None:
        raise BrowserNotFound(browser_id)

    return browsers
