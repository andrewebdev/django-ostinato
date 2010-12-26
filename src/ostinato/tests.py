from django.test import TestCase
from django.contrib.flatpages.models import FlatPage

from ostinato.models import ContentItem

class CMSTestCase(TestCase):
    def setUp(self):
        # Create some basic test content
        self.homepage = FlatPage.objects.create(
            url="/",
            title="Home",
            content="Lorem Ipsum dolor set..."
        )
        self.aboutus = FlatPage.objects.create(
            url="/about-us/",
            title="About Us",
            content="Lorem Ipsum dolor set..."
        )
        self.contact = FlatPage.objects.create(
            url="/contact/",
            title="Contact Us",
            content="Lorem Ipsum dolor set..."
        )

        # Define a standard ContentItem
        self.os_homepage = ContentItem.objects.create(
            title="Home",
            description="The Home Page",
            location="/",
        )
        # Define a ContentItem that points directly to another
        # ContentType
        self.os_aboutus = ContentItem.objects.create_for(
            self.aboutus,
            title="About Us",
            short_title="About",
            description="About Us Page",
            parent=self.os_homepage,
        )
        # One more standard item
        self.os_contact = ContentItem.objects.create(
            title="Contact Us",
            short_title="Contact",
            description="Contact us page",
            location="/contact/",
            parent=self.os_homepage,
        )

class ContentItemTestCase(CMSTestCase):
    def testURL(self):
        self.assertEquals(self.os_homepage.get_absolute_url(), '/')

    def testNavBar(self):
        root = ContentItem.objects.get_navbar()
        self.assertEquals(
            root,
            [{'title': 'Home', 'url': '/'}],
        )
        sub = ContentItem.objects.get_navbar(parent=self.os_homepage)
        self.assertEquals(
            sub,
            [{'title': 'About', 'url': '/about-us/'},
             {'title': 'Contact', 'url': '/contact/'}],
        )

    def testBreadCrumbs(self):
        crumbs = ContentItem.objects.get_breadcrumbs(self.os_aboutus)
        self.assertEquals(
            crumbs,
            [{'title': 'Home', 'url': '/', 'current': False},
             {'title': 'About', 'url': '/about-us/',
              'current': True}
            ]
        )

## Doctests are nice for documentation :)
__test__ = {
"doctest": """

First we create some flatpages which will be our content to work with.

    >>> homepage = FlatPage.objects.create(url="/", title="Home",
    ...     content="Lorem Ipsum dolor set...")
    >>> aboutus = FlatPage.objects.create(url="/about-us/", title="About Us",
    ...     content="Lorem Ipsum dolor set...")
    >>> contact = FlatPage.objects.create(url="/contact/", title="Contact Us",
    ...     content="Lorem Ipsum dolor set...")

We can create ContentItem instances, and specify the location for these
items.

    >>> os_homepage = ContentItem.objects.create(title="Home",
    ...     description="The Home Page", location="/")
    >>> os_contact = ContentItem.objects.create(title="Contact Us",
    ...     short_title="Contact", description="Contact us page",
    ...     location="/contact/", parent=os_homepage, order=2)

We can also create a ContentItem that is generically related to another
ContentType, like a flatpage.

    >>> os_aboutus = ContentItem.objects.create_for(aboutus, title="About Us",
    ...     short_title="About", description="About Us Page",
    ...     parent=os_homepage)

The url for a ContentItem can be looked up using ``get_absolute_url()``

    >>> os_homepage.get_absolute_url()
    '/'
    >>> os_contact.get_absolute_url()
    '/contact/'
    >>> os_aboutus.get_absolute_url()
    u'/about-us/'

ContentItem.get_absolute_url() is 'smart'. If the ContentItem is
generically related to another contenttype that has a
``get_absolute_url()`` method, then it will automatically use the url
returned from that original method. If it cannot find a
get_absolute_url() method on the target contenttype, then it will fall
back to the url specified in the ``location`` field.

Ostinato also provides a way to return ContentItems as a Nav, sitemap and
breadcrumbs.

To get the root navbar you use the manager method ``get_navbar()`` without any
arguments.

    >>> root_nav = ContentItem.objects.get_navbar()
    >>> root_nav
    [{'url': u'/', 'title': u'Home'}]

We can also request a navbar from a specific level, by passing the
``ContentItem`` instance as the ``parent`` argument.

    >>> home_nav = ContentItem.objects.get_navbar(parent=os_homepage)
    >>> home_nav
    [{'url': u'/about-us/', 'title': u'About'}, {'url': u'/contact/', 'title': u'Contact'}]

The statemachine.

ContentItems come with an attached statemachine so that we can create custom
workflows.

Example API Usage.

    >>> os_homepage.state
    u'private'
    >>> os_homepage.get_actions()
    ['submit', 'publish']

We can perform an action on the ContentItem, and it will move to the next state.
Note that thiss will also send pre- and post action signals which you can use
for email notifications etc.

    >>> os_homepage.do_action('submit')
    >>> os_homepage.state
    'review'

If you try perform an action that isn't available to the current state, a
``InvalidAction`` Exception will be raised.

"""}
