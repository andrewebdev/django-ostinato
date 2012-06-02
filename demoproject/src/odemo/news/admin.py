from django.contrib import admin

from ostinato.statemachine.forms import sm_form_factory
from odemo.news.models import NewsItem, NewsWorkflow


class NewsItemAdmin(admin.ModelAdmin):
    # Custom form to include the statemachine
    form = sm_form_factory(NewsWorkflow, state_field='state')

    list_display = ('title', 'state', 'publish_date')
    list_filter = ('state',)
    date_hierarchy = 'publish_date'


admin.site.register(NewsItem, NewsItemAdmin)