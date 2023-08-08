#!/usr/bin/env python
# coding: utf-8

import os
import setuptools


#: The name of the package on PyPi
PYPI_PACKAGE_NAME = 'oa_pynput'

#: The name of the main Python package
MAIN_PACKAGE_NAME = 'oa_pynput'

#: The package URL
PACKAGE_URL = 'https://github.com/OpenAdaptAI/pynput'

#: The author email
AUTHOR_EMAIL = 'moses.palmer@gmail.com'

#: The runtime requirements
RUNTIME_PACKAGES = [
    'six']

#: Additional requirements used during setup
SETUP_PACKAGES = [
    'setuptools-lint >=0.5',
    'sphinx >=1.3.1']

#: Packages requires for different environments
EXTRA_PACKAGES = {
    ':sys_platform == "darwin"': [
        'pyobjc-framework-ApplicationServices >=8.0',
        'pyobjc-framework-Quartz >=8.0'],
    ':"linux" in sys_platform': [
        'evdev >= 1.3',
        'python-xlib >= 0.17'],
    ':python_version == "2.7"': [
        'enum34']}


# Read globals from ._info without loading it
INFO = {}
with open(os.path.join(
        os.path.dirname(__file__),
        'lib',
        MAIN_PACKAGE_NAME,
        '_info.py'), 'rb') as f:
    for line in f.read().decode('utf-8').splitlines():
        try:
            name, value = (i.strip() for i in line.split('='))
            if name.startswith('__') and name.endswith('__'):
                INFO[name[2:-2]] = eval(value)
        except ValueError:
            pass


# Load the read me
with open("README.md", "r", encoding="utf-8") as fh:
    README = fh.read()


setuptools.setup(
    name=PYPI_PACKAGE_NAME,
    version='.'.join(str(i) for i in INFO['version']),
    description='Monitor and control user input devices',
    long_description=README,
    long_description_content_type='text/markdown', 

    install_requires=RUNTIME_PACKAGES,
    setup_requires=RUNTIME_PACKAGES + SETUP_PACKAGES,
    extras_require=EXTRA_PACKAGES,

    author=INFO['author'],
    author_email=AUTHOR_EMAIL,

    url=PACKAGE_URL,

    packages=setuptools.find_packages(
        os.path.join(
            os.path.dirname(__file__),
            'lib')),
    package_dir={'': 'lib'},
    zip_safe=True,

    test_suite='tests',

    license='LGPLv3',
    keywords='control mouse, mouse input, control keyboard, keyboard input',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 '
        '(LGPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Monitoring'])
