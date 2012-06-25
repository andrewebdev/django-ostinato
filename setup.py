from distutils.core import setup

version = '.'.join([str(i) for i in __import__('ostinato').VERSION])

setup(
    name='django-ostinato',
    version=version,
    url='http://django-ostinato.readthedocs.org/en/latest/index.html',
    description='Django-ostinato brings cms-like features to your django projects.',
    author='Andre Engelbrecht',
    author_email='andre@teh-node.co.za',
    download_url='https://github.com/andrewebdev/django-ostinato/tarball/master',
    packages=[
        'ostinato',
        'ostinato.pages',
        'ostinato.statemachine',
        'ostinato.contentfilters',
    ],
    keywords=['django', 'cms', 'ostinato'],
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

