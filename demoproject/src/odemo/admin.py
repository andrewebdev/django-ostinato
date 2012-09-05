from django.contrib import admin

from odemo.models import Contributor


class ContributorInline(admin.StackedInline):
    model = Contributor


