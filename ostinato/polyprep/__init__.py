import re
from django.template import base

"""
    The following prepares the django template tags to explicitly
    require a space in the start and end template variable tags.

    This will allow us to mix polymer and django templates without
    the need for {% verbatim %} if we need to use polymer syntax.

    So after adding this app, make sure that ...

    * ... you use a space for django variables, ie: "{{ somevar }}" and ...
    * ... you do not use spaces in polymer tags, ie: "{{somepolymervar}}"

    h2. Usage

    To use this app just add the following to your settings.py

    ``import ostinato.polyprep``
"""

base.VARIABLE_TAG_START = '{{ '
base.VARIABLE_TAG_END = ' }}'
base.tag_re = (re.compile('(%s.*?%s|%s.*?%s|%s.*?%s)' % (
    re.escape(base.BLOCK_TAG_START), re.escape(base.BLOCK_TAG_END),
    re.escape(base.VARIABLE_TAG_START), re.escape(base.VARIABLE_TAG_END),
    re.escape(base.COMMENT_TAG_START), re.escape(base.COMMENT_TAG_END)
)))

