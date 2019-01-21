from django.test import TestCase
from .factories import PhotoFactory


class MediaLibraryModelTestCase(TestCase):

    def test_media_model(self):
        PhotoFactory.create()
