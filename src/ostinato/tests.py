from django.test import TestCase

from ostinato.models import ContentItem, BasicPage
from ostinato.core import OstinatoCMS, register_apps


class CMSTestCase(TestCase):

    def test_register_and_unregister_model(self):
        self.assertEquals(0, ContentItem.objects.all().count())
        OstinatoCMS.register(BasicPage)

        page = BasicPage(title="BasicPage 1", content="BasicPage 1 Content")
        page.save()
        self.assertEquals(1, ContentItem.objects.all().count())

        OstinatoCMS.unregister(BasicPage) ## Need this for some cleanup
        page2 = BasicPage(title="BasicPage 2", content="BasicPage 2 Content")
        self.assertEquals(1, ContentItem.objects.all().count())

    def test_register_apps(self):
        register_apps()

        self.assertEquals(0, ContentItem.objects.all().count())

        page = BasicPage(title="page1", content="page 1 content")
        page.save()
        self.assertEquals(1, ContentItem.objects.all().count())

        OstinatoCMS.unregister(BasicPage) ## Need this for some cleanup


class StateMachineTestCase(TestCase):

    def setUp(self):
        OstinatoCMS.register(BasicPage)
        page1 = BasicPage.objects.create(
            title="BasicPage 1", content="Basic Page 1 Content")
        OstinatoCMS.unregister(BasicPage)

    def test_content_item_default_state(self):
        content_item = ContentItem.objects.all()[0]
        self.assertEqual('Private', content_item.sm_state)

    ## Test Statemachine Actions

    ## Statemachine Actions Callbacks


class ContentItemTestCase(TestCase):

    def setUp(self):
        OstinatoCMS.register(BasicPage)

        page1 = BasicPage.objects.create(
            title="BasicPage 1", content="Basic Page 1 Content")
        page2 = BasicPage.objects.create(
            title="BasicPage 2", content="Basic Page 2 Content")
        page3 = BasicPage.objects.create(
            title="BasicPage 3", content="Basic Page 3 Content")

    def test_content_item_prepopulated_fields(self):
        """
        Some of the fields in the content item are guessed and prepopulated
        from the registered model. Check this here.
        """
        content_item = ContentItem.objects.all()[0]
        self.assertEqual('BasicPage 1', content_item.title)
        self.assertEqual('basicpage-1', content_item.slug)


# __test__ = {
# "doctest": """

# First we create some flatpages which will be our content to work with.

#     >>> homepage = FlatPage.objects.create(url="/", title="Home",
#     ...     content="Lorem Ipsum dolor set...")
#     >>> aboutus = FlatPage.objects.create(url="/about-us/", title="About Us",
#     ...     content="Lorem Ipsum dolor set...")
#     >>> contact = FlatPage.objects.create(url="/contact/", title="Contact Us",
#     ...     content="Lorem Ipsum dolor set...")

# We can create ContentItem instances, and specify the location for these
# items.

#     >>> os_homepage = ContentItem.objects.create(title="Home",
#     ...     description="The Home Page", location="/")
#     >>> os_contact = ContentItem.objects.create(title="Contact Us",
#     ...     short_title="Contact", description="Contact us page",
#     ...     location="/contact/", parent=os_homepage, order=2)

# We can also create a ContentItem that is generically related to another
# ContentType, like a flatpage.

#     >>> os_aboutus = ContentItem.objects.create_for(aboutus, title="About Us",
#     ...     short_title="About", description="About Us Page",
#     ...     parent=os_homepage)

# The url for a ContentItem can be looked up using ``get_absolute_url()``

#     >>> os_homepage.get_absolute_url()
#     '/'
#     >>> os_contact.get_absolute_url()
#     '/contact/'
#     >>> os_aboutus.get_absolute_url()
#     u'/about-us/'

# ContentItem.get_absolute_url() is 'smart'. If the ContentItem is
# generically related to another contenttype that has a
# ``get_absolute_url()`` method, then it will automatically use the url
# returned from that original method. If it cannot find a
# get_absolute_url() method on the target contenttype, then it will fall
# back to the url specified in the ``location`` field.

# Ostinato also provides a way to return ContentItems as a Nav, sitemap and
# breadcrumbs.

# To get the root navbar you use the manager method ``get_navbar()`` without any
# arguments.

#     >>> root_nav = ContentItem.objects.get_navbar()
#     >>> root_nav
#     [{'url': u'/', 'title': u'Home'}]

# We can also request a navbar from a specific level, by passing the
# ``ContentItem`` instance as the ``parent`` argument.

#     >>> home_nav = ContentItem.objects.get_navbar(parent=os_homepage)
#     >>> home_nav
#     [{'url': u'/about-us/', 'title': u'About'}, {'url': u'/contact/', 'title': u'Contact'}]

# The statemachine.

# ContentItems come with an attached statemachine so that we can create custom
# workflows.

# Example API Usage.

#     >>> os_homepage.sm_state
#     u'Private'
#     >>> os_homepage.sm_state_actions()
#     ['Submit', 'Publish']

# We can perform an action on the ContentItem, and it will move to the next state.
# Note that thiss will also send pre- and post action signals which you can use
# for email notifications etc.

#     >>> os_homepage.sm_take_action('Submit')
#     >>> os_homepage.sm_state
#     'Review'
#     >>> os_homepage.sm_state_actions()
#     ['Publish', 'Reject']

# If you try perform an action that isn't available to the current state, a
# ``InvalidAction`` Exception will be raised.

# """}
