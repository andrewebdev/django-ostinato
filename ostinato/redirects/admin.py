from django.contrib import admin
from .models import Redirect


@admin.register(Redirect)
class RedirectAdmin(admin.ModelAdmin):
    list_display = ('old_path', 'new_path', 'code')
    list_filter = ('code',)
    search_field = ('old_path', 'new_path')
