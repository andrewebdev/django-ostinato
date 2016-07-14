import factory
from factory.django import DjangoModelFactory

from ..models import Photo


class PhotoFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: "Media {0} Title")
    caption = factory.Sequence(lambda n: "Media {0} Caption")
    order = 0
    is_visible = True

    class Meta:
        model = Photo
