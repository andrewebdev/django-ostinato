import os
import collections.abc
from functools import reduce
from ruamel.yaml import YAML
try:
    from jinja2 import Environment, FileSystemLoader
    NO_JINJA = False
except ImportError:
    NO_JINJA = True


def merge_dicts(base, merge_dict):
    """
    Safely merges nested dictionaries
    """
    for k, v in merge_dict.items():
        if isinstance(v, collections.abc.Mapping):
            base[k] = merge_dicts(base.get(k, {}), v)
        else:
            base[k] = v
    return base


class ConfigManager(object):
    """
    Our re-usable environment settings manager used in all my Projects

    Example Usage:

    >>> conf = ConfigManager('env.yml', local_settings='local.yml', templates_dir='templates')
    >>> conf.make_dirs([
        'share/traefik/certs:0o600',
        'logs',
    ])
    >>> conf.render_template('docker-compose.yml.j2', 'docker-compose.yml')
    >>> conf.get('some.setting.path', 'default')
    """
    def __init__(self, filename, local_settings=None, templates_dir=None):
        if templates_dir is not None and not NO_JINJA:
            self._env = Environment(loader=FileSystemLoader(templates_dir))
        else:
            self._env = None

        with open(filename, 'r') as base_file:
            self._conf = YAML().load(base_file)

        if local_settings is not None and os.path.exists(local_settings):
            with open(local_settings, 'r') as local_file:
                merge_conf = YAML().load(local_file)
                if merge_conf:
                    self._conf = merge_dicts(self._conf, merge_conf)

    def get(self, key=None, default=None):
        """
        Returns the value for the key path
        """
        if key is None:
            return self._conf
        try:
            return reduce(lambda c, k: c[k], key.split('.'), self._conf)
        except KeyError:
            return default

    def render_template(self, template_name, out_file, context=None):
        """
        Renders a jinja template
        """
        if NO_JINJA:
            raise Exception("Cannot render templates; Jinja2 not installed")
        if context is None:
            context = self._conf
        template = self._env.get_template(template_name)
        template.stream(**context).dump(out_file)

    def make_dirs(self, dir_list):
        """
        Makes directories. Directory permissions can be specified by appending
        `:<octal_permission_code>` after the directory. eg.

            conf.make_dirs(['temp/test:0o600'])

        """
        for dpath in dir_list:
            try:
                dpath, mode = dpath.split(':')
                os.makedirs(dpath, mode=int(mode, 8), exist_ok=True)
            except ValueError:
                os.makedirs(dpath, exist_ok=True)
