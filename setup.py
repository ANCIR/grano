import os
from setuptools import setup, find_packages

README = os.path.join(os.path.dirname(__file__), 'README.rst')

REQUIREMENTS = os.path.join(os.path.dirname(__file__), 'requirements.txt')
REQUIREMENTS = open(REQUIREMENTS, 'r').read().splitlines()

VERSION = os.path.join(os.path.dirname(__file__), 'VERSION')
VERSION = open(VERSION, 'r').read().strip()

setup(
    name='grano',
    version=VERSION,
    description="An investigative toolkit for influence influence mapping",
    long_description=open(README, 'r').read(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
    keywords='sql graph sna networks journalism ddj entities',
    author='Code for Africa',
    author_email='support@codeforafrica.org',
    url='http://github.com/CodeForAfrica/grano',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['grano'],
    package_data={'grano': ['fixtures/base.yaml']},
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    dependency_links=[
        'https://github.com/CodeForAfrica/grano-client/tarball/master#egg=grano-client'
    ],
    entry_points={
        'grano.entity.change': [],
        'grano.relation.change': [],
        'grano.project.change': [],
        'grano.schema.change': [],
        'grano.startup': [
            'bidi_create = grano.query.bidi:GenerateBidi',
            'levenshtein = grano.logic.reconcile:ConfigurePostgres'
        ],
        'grano.periodic': [
            'degrees = grano.logic.metrics:Degrees',
            'bidi_refresh = grano.query.bidi:GenerateBidi'
        ],
        'console_scripts': [
            'grano = grano.manage:run',
        ]
    },
    tests_require=[],
    test_suite='grano.test'
)
