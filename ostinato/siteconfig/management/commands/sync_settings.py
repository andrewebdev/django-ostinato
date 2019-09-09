from django.core.management.base import BaseCommand
from ostinato.siteconfig.models import sync_settings


class Command(BaseCommand):
    args = ''
    help = 'Sync custom settings with the site settings.'

    def handle(self, *args, **kwargs):
        sync_settings()
