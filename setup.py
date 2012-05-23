from distutils.core import setup

version = '.'.join([str(i) for i in __import__('ostinato').VERSION])

setup(
    name="django-ostinato",
    version=version,
    url="",
    description="Django-ostinato brings common CMS features to pluggable django apps",
    author="Andre Engelbrecht",
    author_email="andre@teh-node.co.za",
    packages=['ostinato'],
    install_requires=[
        'setuptools',
        'django-mptt == 0.5.2',
    ],
)

