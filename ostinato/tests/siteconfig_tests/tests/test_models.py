from decimal import Decimal
from django.test import TestCase
from ostinato.siteconfig.models import (
    Setting,
    sync_settings,
)


class SettingModelTestCase(TestCase):

    def test_sync_settings(self):
        self.assertEqual(0, Setting.objects.all().count())
        sync_settings()
        all_settings = Setting.objects.all()
        self.assertEqual(4, all_settings.count())

    def test_string_type(self):
        sync_settings()
        conf = Setting.objects.all()[0]
        self.assertEqual('site.globalmessage', conf.setting_key)
        self.assertEqual('str', conf.value_type)
        self.assertEqual('Hello', conf.value)

        # Only need to test this once
        self.assertEqual('site.globalmessage', str(conf))

    def test_integer_type(self):
        sync_settings()
        conf = Setting.objects.all()[1]
        self.assertEqual('site.integer', conf.setting_key)
        self.assertEqual('int', conf.value_type)
        self.assertEqual(100, conf.value)

    def test_decimal_type(self):
        sync_settings()
        conf = Setting.objects.all()[2]
        self.assertEqual('site.decimal', conf.setting_key)
        self.assertEqual('dec', conf.value_type)
        self.assertEqual(Decimal('200.33'), conf.value)

    def test_boolean_type(self):
        sync_settings()
        conf = Setting.objects.all()[3]
        self.assertEqual('site.boolean', conf.setting_key)
        self.assertEqual('bool', conf.value_type)
        self.assertTrue(conf.value)

    def test_settings_map(self):
        sync_settings()
        self.assertEqual({
            'site.globalmessage': 'Hello',
            'site.integer': 100,
            'site.decimal': Decimal('200.33'),
            'site.boolean': True,
        }, Setting.objects.settings_map())
