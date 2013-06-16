from ostinato.pages.registry import PageTemplate, page_templates


@page_templates.register
class LandingPageTemplate(PageTemplate):
    form = 'website.forms.LandingPageTemplateForm'
    page_content = [
        'ostinato.pages.models.MetaContent',
        'website.models.RichContent',
    ]


@page_templates.register
class GenericPageTemplate(PageTemplate):
    page_content = [
        'ostinato.pages.models.MetaContent',
        'website.models.RichContent',
    ]


@page_templates.register
class ListTemplate(PageTemplate):
    page_content = [
        'ostinato.pages.models.MetaContent',
    ]


@page_templates.register
class CaseStudyTemplate(PageTemplate):
    page_content = [
        'ostinato.pages.models.MetaContent',
        'website.models.RichContent',
    ]


@page_templates.register
class ContactFormTemplate(PageTemplate):
    page_content = [
        'ostinato.pages.models.MetaContent',
        'website.models.RichContent',
        'website.models.ContactFormContent',
    ]
