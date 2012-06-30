from django.core.management.base import BaseCommand
from django.db.models import get_models, get_app
from django.contrib.auth.management import create_permissions


class Command(BaseCommand):
    args = '<app app ...>'
    help = 'reloads permissions for specified apps.'

    def handle(self, *args, **options):

        apps = []
        for arg in args:
            apps.append(get_app(arg))

        for app in apps:
            create_permissions(app, None, options.get('verbosity', 0))
    
