#!/usr/bin/env python

import sys
import os
from os.path import abspath, join, dirname
from subprocess import list2cmdline
from distutils.core import setup
from distutils.command.install_scripts import install_scripts

try:
    import setuptools    # use setuptools when available
except ImportError:
    pass

CURDIR = dirname(abspath(__file__))

with open(join(CURDIR, 'src', 'robot', 'version.py')) as f:
    exec(f.read())
    VERSION = get_version()
with open(join(CURDIR, 'README.rst')) as f:
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
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: Jython
Programming Language :: Python :: Implementation :: IronPython
Topic :: Software Development :: Testing
Framework :: Robot Framework
""".strip().splitlines()
KEYWORDS = 'robotframework testing testautomation acceptancetesting atdd bdd'
PACKAGES = ['robot', 'robot.api', 'robot.conf', 'robot.htmldata',
            'robot.libdocpkg', 'robot.libraries', 'robot.model',
            'robot.output', 'robot.output.console', 'robot.parsing',
            'robot.reporting', 'robot.result', 'robot.running',
            'robot.running.arguments', 'robot.running.timeouts',
            'robot.utils', 'robot.variables', 'robot.writer']
PACKAGE_DATA = [join('htmldata', directory, pattern)
                for directory in ('rebot', 'libdoc', 'testdoc', 'lib', 'common')
                for pattern in ('*.html', '*.css', '*.js')]
WINDOWS = os.sep == '\\'
if sys.platform.startswith('java'):
    SCRIPTS = ['jybot', 'jyrebot']
elif sys.platform == 'cli':
    SCRIPTS = ['ipybot', 'ipyrebot']
else:
    SCRIPTS = ['pybot']
SCRIPTS = [join('src', 'bin', s) for s in SCRIPTS + ['robot', 'rebot']]
if WINDOWS:
    SCRIPTS = [s+'.bat' for s in SCRIPTS]


class custom_install_scripts(install_scripts):

    def run(self):
        install_scripts.run(self)
        if WINDOWS:
            self._replace_interpreter_in_bat_files()

    def _replace_interpreter_in_bat_files(self):
        print("replacing interpreter in robot.bat and rebot.bat.")
        interpreter = list2cmdline([sys.executable])
        for path in self.get_outputs():
            if path.endswith(('robot.bat', 'rebot.bat')):
                with open(path, 'r') as input:
                    replaced = input.read().replace('python', interpreter)
                with open(path, 'w') as output:
                    output.write(replaced)


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
    cmdclass     = {'install_scripts': custom_install_scripts}
)
