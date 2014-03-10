from setuptools import setup, find_packages
import os

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='grano',
    version='0.3.1',
    description="An entity and social network tracking software for news applications",
    long_description=open('README.rst').read(),
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
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    install_requires=required,
    entry_points={
        'grano.entity.change': [
    #        'indexer = grano.logic.indexer:AutoIndexer'
        ],
        'console_scripts': [
            'grano = grano.manage:run',
        ]
    },
    tests_require=[]
)
