from .factories import (
    PageFactory,
    LandingPageFactory,
)


def create_pages():
    p = PageFactory.create(
        title="Page 1",
        slug="page-1",
        template='pages.landingpage'
    )
    PageFactory.create(
        title="Page 2",
        slug="page-2",
        short_title='P2',
        template='pages.basicpage'
    )
    PageFactory.create(
        title="Page 3",
        slug="page-3",
        short_title='Page 3',
        template='pages.basicpage',
        parent=p
    )
    PageFactory.create(
        title="Page 4",
        slug="func-page",
        show_in_nav=False,
        template='pages.basicpagefunc'
    )

    # Create some content
    LandingPageFactory.create(
        page=p,
        intro='Page 1 Introduction',
        content='Page 1 Content'
    )
