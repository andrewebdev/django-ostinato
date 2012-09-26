from django.contrib.sitemaps import Sitemap

from ostinato.pages.models import Page


class PageSitemap(Sitemap):
    changefreq = 'never'
    priority = 0.5

    def items(self):
        return Page.objects.published().filter(show_in_sitemap=True)

    def lastmod(self, obj): 
        return obj.modified_date

