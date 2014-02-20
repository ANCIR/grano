from setuptools import setup, find_packages

setup(
    name='grano',
    version='0.3',
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
    url='http://grano.pudo.org',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=[],
    include_package_data=False,
    zip_safe=False,
    install_requires=[
    ],
    entry_points={
        'grano.entity.change': [
            'indexer = grano.service.indexer:AutoIndexer'
        ],
        'console_scripts': [
            'grano = grano.manage:run',
        ]
    },
    tests_require=[]
)
