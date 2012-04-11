from distutils.core import setup

setup(
    name="django-ostinato",
    description="Django-ostinato brings common CMS features to pluggable django apps",
    version="0.4.3",
    url="",
    author="Andre Engelbrecht",
    author_email="andre@teh-node.co.za",
    packages=['ostinato'],
    package_dir={'': 'src'},
    install_requires=[
        'setuptools',
        'mptt == 0.5.2',
        'django-appregister == 0.2',
    ]
)
