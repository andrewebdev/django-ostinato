from setuptools import setup, find_packages

setup(
    name="django-ostinato",
    version="0.6.1",
    url="",
    description="Django-ostinato brings common CMS features to pluggable django apps",
    author="Andre Engelbrecht",
    author_email="andre@teh-node.co.za",
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'setuptools',
        'django-mptt == 0.5.2',
    ],
)

