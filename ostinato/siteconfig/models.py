from decimal import Decimal
from django.db import models
from django.conf import settings


def sync_settings():
    SITECONFIG_SETTINGS = getattr(settings, 'SITECONFIG_SETTINGS', None)
    for s in SITECONFIG_SETTINGS:
        obj, created = Setting.objects.get_or_create(setting_key=s[0])
        obj.value_type = s[1]
        if created:
            try:
                obj.setting_value = s[2]
            except IndexError:
                obj.setting_value = ''
        obj.save()


class SettingManager(models.Manager):

    def settings_map(self):
        # TODO: Since these values change so seldomly, we should have it
        # cached using django's cache api.
        m = dict()
        all_settings = self.get_queryset().all()
        for s in all_settings:
            m[s.setting_key] = s.value
        return m


class Setting(models.Model):
    VALUE_TYPE_CHOICES = (
        ('str', 'String'),
        ('int', 'Integer Number'),
        ('dec', 'Decimal Number'),
        ('bool', 'Boolean (yes/no)'),
    )

    # These two fields are created by the developer and/or code if it doesn't
    # exist.
    setting_key = models.CharField(max_length=200, unique=True)
    value_type = models.CharField(
        max_length=25,
        choices=VALUE_TYPE_CHOICES,
        default='string')

    # readonly = models.BooleanField(default=False)

    # This is the only field that the editors will be able to edit, if they
    # have the permissions to do so.
    setting_value = models.TextField(null=True, blank=True)

    objects = SettingManager()

    def __str__(self):
        return self.setting_key

    def delete(self, *args, **kwargs):
        """
        Override so that we can disable this. These settings should never
        be deleted.
        """
        pass

    @property
    def value(self):
        if self.value_type == 'int':
            return int(self.setting_value)
        elif self.value_type == 'dec':
            return Decimal(self.setting_value)
        elif self.value_type == 'bool':
            return self.setting_value in ['yes']
        else:
            return self.setting_value
