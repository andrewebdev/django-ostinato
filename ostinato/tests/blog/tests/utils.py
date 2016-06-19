from django.contrib.auth.models import User
from ..models import Entry


def create_objects():
    u = User.objects.create(
        username='user1', password='', email='test@example.com')

    Entry.objects.create(
        title='Entry Title 1',
        slug='entry-title-1',
        content='Entry Content 1',
        author=u,
    )

    Entry.objects.create(
        title='Entry Title 2',
        slug='entry-title-2',
        content='Entry Content 2',
        author=u,
    )

    Entry.objects.create(
        title='Entry Title 3',
        slug='entry-title-3',
        content='Entry Content 3',
        author=u,
    )

