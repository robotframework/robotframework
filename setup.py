#!/usr/bin/env python

import sys
import os
from os.path import abspath, join, dirname
from distutils.core import setup

try:
    import setuptools    # use setuptools when available
except ImportError:
    pass

CURDIR = dirname(abspath(__file__))

execfile(join(CURDIR, 'src', 'robot', 'version.py'))
VERSION = get_version()
with open(join(CURDIR, 'README.rst')) as readme:
    install = 'https://github.com/robotframework/robotframework/blob/master/INSTALL.rst'
    LONG_DESCRIPTION = readme.read().replace(
        '`<INSTALL.rst>`__', '`INSTALL.rst <%s>`__' % install)
CLASSIFIERS = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Testing
""".strip().splitlines()
KEYWORDS = 'robotframework testing testautomation acceptancetesting atdd bdd'
# Maximum width in Windows installer seems to be 70 characters -------|
WINDOWS_DESCRIPTION = """
Robot Framework is a generic test automation framework for acceptance
testing and acceptance test-driven development (ATDD). It has
easy-to-use tabular test data syntax and utilizes the keyword-driven
testing approach. Its testing capabilities can be extended by test
libraries implemented either with Python or Java, and users can create
new keywords from existing ones using the same syntax that is used for
creating test cases.
""".strip()
PACKAGES = ['robot', 'robot.api', 'robot.conf', 'robot.htmldata',
            'robot.libdocpkg', 'robot.libraries', 'robot.model',
            'robot.output', 'robot.output.console', 'robot.parsing',
            'robot.reporting', 'robot.result', 'robot.running',
            'robot.running.arguments', 'robot.running.timeouts',
            'robot.utils', 'robot.variables', 'robot.writer']
PACKAGE_DATA = [join('htmldata', directory, pattern)
                for directory in 'rebot', 'libdoc', 'testdoc', 'lib', 'common'
                for pattern in '*.html', '*.css', '*.js']
if sys.platform.startswith('java'):
    SCRIPTS = ['jybot', 'jyrebot']
elif sys.platform == 'cli':
    SCRIPTS = ['ipybot', 'ipyrebot']
else:
    SCRIPTS = ['pybot', 'rebot']
SCRIPTS = [join('src', 'bin', s) for s in SCRIPTS]
if os.sep == '\\':
    SCRIPTS = [s+'.bat' for s in SCRIPTS]
if 'bdist_wininst' in sys.argv:
    SCRIPTS.append('robot_postinstall.py')
    LONG_DESCRIPTION = WINDOWS_DESCRIPTION

setup(
    name         = 'robotframework',
    version      = VERSION,
    author       = 'Robot Framework Developers',
    author_email = 'robotframework@gmail.com',
    url          = 'http://robotframework.org',
    download_url = 'https://pypi.python.org/pypi/robotframework',
    license      = 'Apache License 2.0',
    description  = 'A generic test automation framework',
    long_description = LONG_DESCRIPTION,
    keywords     = KEYWORDS,
    platforms    = 'any',
    classifiers  = CLASSIFIERS,
    package_dir  = {'': 'src'},
    package_data = {'robot': PACKAGE_DATA},
    packages     = PACKAGES,
    scripts      = SCRIPTS,
)
