from ostinato.pages.registry import PageTemplate, page_templates


@page_templates.register
class LandingPageTemplate(PageTemplate):
    page_content = [
        'ostinato.pagecontent.models.MetaContent',
        'website.models.RichContent',
    ]


@page_templates.register
class GenericPageTemplate(PageTemplate):
    page_content = [
        'ostinato.pagecontent.models.MetaContent',
        'website.models.RichContent',
    ]


@page_templates.register
class ListTemplate(PageTemplate):
    page_content = [
        'ostinato.pagecontent.models.MetaContent',
    ]


@page_templates.register
class CaseStudyTemplate(PageTemplate):
    page_content = [
        'ostinato.pagecontent.models.MetaContent',
        'website.models.RichContent',
    ]


@page_templates.register
class ContactFormTemplate(PageTemplate):
    view = 'ostinato.pagecontent.views.ContactPageView'
    template = 'pages/contact_page.html'
    page_content = [
        'ostinato.pagecontent.models.MetaContent',
        'website.models.RichContent',
        'ostinato.pagecontent.models.ContactFormContent',
    ]
