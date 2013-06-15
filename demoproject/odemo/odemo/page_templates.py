from ostinato.pages.registry import PageTemplate, page_templates


@page_templates.register
class LandingPageTemplate(PageTemplate):
    page_content = ['ostinato.pages.models.MetaContent']
    # OR
    page_content = ['pages.metacontent']
