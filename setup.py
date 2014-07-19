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
    author='Friedrich Lindenberg',
    author_email='friedrich@pudo.org',
    url='http://docs.grano.cc',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages = ['grano'],
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    entry_points={
        'grano.entity.change': [],
        'grano.relation.change': [],
        'grano.startup': [],
        'console_scripts': [
            'grano = grano.manage:run',
        ]
    },
    tests_require=[],
    test_suite='grano.test'
)
