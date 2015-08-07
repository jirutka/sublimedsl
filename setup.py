#!/usr/bin/env python3

from sublimedsl import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(
    name='sublimedsl',
    version=__version__,
    url='https://github.com/jirutka/sublimedsl',
    description='A convenient DSL for generating SublimeText configs.',
    long_description=read_md('README.md'),
    author='Jakub Jirutka',
    author_email='jakub@jirutka.cz',
    license='MIT',
    packages=['sublimedsl'],
    scripts=[],
    install_requires=['funcy>=1.0'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ],
)
