from setuptools import setup, find_packages

setup(
    name='grano',
    version='0.1',
    description="A entity tracking software for news organisations",
    long_description='',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ],
    keywords='sql graph sna networks journalism ddj entities',
    author='Friedrich Lindenberg',
    author_email='friedrich@pudo.org',
    url='http://pudo.org',
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
    },
    tests_require=[]
)
