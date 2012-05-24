from django.test import TestCase

from ostinato.contentfilters import ContentMod
from ostinato.contentfilters.templatetags.content_filters import modify


def test_func(content):
    # convert everything to uppercase
    return content.upper()

def test_func_2(content):
    # add an exclamation mark at end
    return content + '!'

def test_func_3(content):
    # Add 123_ to the start
    return '123_' + content


class ContentModTestCase(TestCase):
    """ Tests for the Content Modifier Class """

    def clear_mods(self):
        ContentMod._modifiers = []

    def add_test_func(self):
        ContentMod.register('test_func', test_func)
        ContentMod.register('test_func_2', test_func_2)
        ContentMod.register('test_func_3', test_func_3)

    def test_class_exists(self):
        ContentMod

    def test_register_class_method(self):
        self.clear_mods()
        self.assertEqual([], ContentMod._modifiers)

        self.add_test_func()
        self.assertEqual([
            {'func': test_func, 'name': 'test_func'},
            {'func': test_func_2, 'name': 'test_func_2'},
            {'func': test_func_3, 'name': 'test_func_3'},
        ], ContentMod._modifiers)

    def test_modifier(self):
        self.clear_mods()
        self.add_test_func()

        cm = ContentMod()
        self.assertEqual([test_func, test_func_2, test_func_3], cm.modifiers())

    def test_modifiers_exclude_list(self):
        self.clear_mods()
        self.add_test_func()

        cm = ContentMod()
        self.assertEqual([test_func_2, test_func_3],
            cm.modifiers(exclude='test_func'))

    def test_getitem(self):
        self.clear_mods()
        self.add_test_func()

        cm = ContentMod()
        self.assertEqual(test_func_2, cm['test_func_2'])

    def test_modify_function_exists(self):
        self.clear_mods()
        self.add_test_func()

        modify('Test Content')

    def test_modify_all(self):
        self.clear_mods()
        self.add_test_func()

        self.assertEqual('123_TEST CONTENT!', modify('Test Content'))

    def test_modify_mod_list(self):
        self.clear_mods()
        self.add_test_func()

        self.assertEqual('123_Test Content!', modify('Test Content',
            mods='test_func_2,test_func_3'))

    def test_modify_exclude_list(self):
        self.clear_mods()
        self.add_test_func()

        self.assertEqual('TEST CONTENT', modify('Test Content',
            mods='!test_func_2,test_func_3'))

