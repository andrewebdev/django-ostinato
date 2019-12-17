from setuptools import find_packages, setup


version = '.'.join([str(i) for i in __import__('ostinato').VERSION])


# Now our setup
setup(
    name='django-ostinato',
    version=version,
    url='http://django-ostinato.readthedocs.org/en/latest/index.html',
    description='Django-ostinato brings cms-like features to your django projects.',
    author='Andre Engelbrecht',
    author_email='andre@tehnode.co.uk',
    license='MIT',
    download_url='https://github.com/andrewebdev/django-ostinato/tarball/master',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'django-mptt == 0.10.0',
    ],
    keywords=['django', 'cms', 'ostinato', 'statemachine', 'pages', 'blog'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
)
