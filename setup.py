import os
from setuptools import setup, find_packages

README = os.path.join(os.path.dirname(__file__), 'README.rst')
REQUIREMENTS = os.path.join(os.path.dirname(__file__), 'requirements.txt')
REQUIREMENTS = open(REQUIREMENTS, 'r').read().splitlines()

setup(
    name='grano',
    version='0.3.2',
    description="An investigative toolkit for influence influence mapping",
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
