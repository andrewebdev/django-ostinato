from django import template
from ostinato.contentfilters import ContentMod

register = template.Library()


def uppercase(content):
    return content.upper()


ContentMod.register('upper', uppercase)

