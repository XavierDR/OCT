from setuptools import setup, find_packages

from os import path

def read_from_file(*filename):
    with open(path.join(*filename), 'r') as f:
        return f.read()

setup(
    name = 'zaber.serial',
    version = '0.7',
    packages = find_packages(exclude=["test*", "test_*", "*_test*"]),
    description = 'A library for communicating with Zaber devices',
    long_description = read_from_file('DESCRIPTION.rst'),
    url = 'http://www.zaber.com/support/docs/api/core-python/',
    author = 'Zaber Technologies Inc.',
    author_email = 'contact@zaber.com',
    license = 'Apache Software License v2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4'
    ],
    keywords = 'serial zaber',

    # This library is built on top of PySerial.
    install_requires=['pyserial'],
    extras_require = { 'test': ['pytest'] }
)
