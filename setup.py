#!/usr/bin/env python

from os.path import abspath, join, dirname
from setuptools import find_packages, setup


# Version number typically updated by running `invoke set-version <version>`.
# Run `invoke --help set-version` or see tasks.py for details.
VERSION = '5.0.dev1'
with open(join(dirname(abspath(__file__)), 'README.rst')) as f:
    LONG_DESCRIPTION = f.read()
    base_url = 'https://github.com/robotframework/robotframework/blob/master'
    for text in ('INSTALL', 'CONTRIBUTING'):
        search = '`<{0}.rst>`__'.format(text)
        replace = '`{0}.rst <{1}/{0}.rst>`__'.format(text, base_url)
        if search not in LONG_DESCRIPTION:
            raise RuntimeError('{} not found from README.rst'.format(search))
        LONG_DESCRIPTION = LONG_DESCRIPTION.replace(search, replace)
CLASSIFIERS = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python :: 3
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Software Development :: Testing
Topic :: Software Development :: Testing :: Acceptance
Topic :: Software Development :: Testing :: BDD
Framework :: Robot Framework
""".strip().splitlines()
DESCRIPTION = ('Generic automation framework for acceptance testing '
               'and robotic process automation (RPA)')
KEYWORDS = ('robotframework automation testautomation rpa '
            'testing acceptancetesting atdd bdd')
PACKAGE_DATA = [join('htmldata', directory, pattern)
                for directory in ('rebot', 'libdoc', 'testdoc', 'lib', 'common')
                for pattern in ('*.html', '*.css', '*.js')]


setup(
    name         = 'robotframework',
    version      = VERSION,
    author       = 'Pekka Kl\xe4rck',
    author_email = 'peke@eliga.fi',
    url          = 'http://robotframework.org',
    download_url = 'https://pypi.python.org/pypi/robotframework',
    license      = 'Apache License 2.0',
    description  = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    long_description_content_type = 'text/x-rst',
    keywords     = KEYWORDS,
    platforms    = 'any',
    classifiers  = CLASSIFIERS,
    package_dir  = {'': 'src'},
    package_data = {'robot': PACKAGE_DATA},
    packages     = find_packages('src'),
    entry_points = {'console_scripts': ['robot = robot.run:run_cli',
                                        'rebot = robot.rebot:rebot_cli',
                                        'libdoc = robot.libdoc:libdoc_cli']}
)
