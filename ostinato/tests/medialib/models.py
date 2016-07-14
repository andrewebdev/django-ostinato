from django.db import models
from ostinato.medialib.models import MediaItem


class Photo(MediaItem):
    image = models.ImageField(upload_to="/")


class Video(MediaItem):
    url = models.URLField()
