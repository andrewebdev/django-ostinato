#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


if __name__ == '__main__':
    os.environ['DJANGO_SETTINGS_MODULE'] = 'ostinato.tests.test_settings'
    django.setup()

    test_runner = get_runner(settings)()
    failures = test_runner.run_tests([
        'ostinato.tests.pages',
        'ostinato.tests.statemachine',
        'ostinato.tests.blog',
        'ostinato.tests.contentfilters',
    ])

    sys.exit(bool(failures))

