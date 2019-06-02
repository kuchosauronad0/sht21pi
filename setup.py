# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='sht21pi',
    version='0.0.5',
    description='Library for sht21pi.',
    long_description=readme,
    author='Andre Poley',
    author_email='andre.poley@mailbox.org',
    url='https://github.com/kuchosauronad0/sht21pi',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
