from django.db import models


class Redirect(models.Model):
    RESPONSE_CODES = (
        (302, "Moved Temporarily"),
        (301, "Moved Permanently"),
        (410, "Gone"),
    )

    old_path = models.CharField(
        max_length=250,
        help_text="Absolute path for old URL, excluding the domain name. "
                  "Example: '/events/search/'.")

    new_path = models.CharField(
        max_length=250,
        blank=True,
        help_text="This can be either an absolute path (as above) or a full "
                  "URL starting with 'http://'.")

    code = models.PositiveSmallIntegerField(
        choices=RESPONSE_CODES,
        default=302)

    def __str__(self):
        return "{} --> {}".format(self.old_path, self.new_path)
