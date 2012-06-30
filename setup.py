import os
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES


version = '.'.join([str(i) for i in __import__('ostinato').VERSION])


### Snippets borrowed from django setup.py ...

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


# Tell distutils not to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
ostinato_dir = 'ostinato'

for dirpath, dirnames, filenames in os.walk(ostinato_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

### End Snippets borrowed from django


# Now our setup
setup(
    name='django-ostinato',
    version=version,
    url='http://django-ostinato.readthedocs.org/en/latest/index.html',
    description='Django-ostinato brings cms-like features to your django projects.',
    author='Andre Engelbrecht',
    author_email='andre@teh-node.co.za',
    license='MIT',
    download_url='https://github.com/andrewebdev/django-ostinato/tarball/master',
    packages=packages,
    data_files=data_files,
    # package_data={
    #     'ostinato': ['fixtures/*', 'static/*'],
    #     'ostinato.pages': ['static/*', 'templates/*'],
    # },
    keywords=['django', 'cms', 'ostinato', 'statemachine', 'pages', 'blog'],
    install_requires=[
        'setuptools',
        'django-mptt == 0.5.2',
        'django-appregister == 0.3.1',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    long_description="""\
Introduction
============

Django-ostinato is a collection of applications that aims to bring together
some of the most common features expected from a CMS.

Please feel free to log any issues on the `Github issue tracker <https://github.com/andrewebdev/django-ostinato/issues>`_.

If you want to track actual progress, as well as a list of features/bugs we
are currently working on, you can do so on our `Pivotal Tracker <https://www.pivotaltracker.com/projects/417365>`_ page.


For more detailed information `read the documentation <http://django-ostinato.readthedocs.org/en/latest/index.html>`_.
"""
)

