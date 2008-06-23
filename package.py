#!/usr/bin/env python

# Copyright 2008 Nokia Siemens Networks Oyj
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Packaging script for Robot Framework

Usage:  python package.py type version release

'type' can be either:
  sdist    - create source distribution
  wininst  - create Windows installer
  all      - create both packages
  version  - update only version information

'version' must be either a version number in format '2.x(.y)' or 'trunk'.

'release' must be 'alpha', 'beta', 'rc' or 'final', where all but the
last one can have a number after the name like 'alpha1' or 'rc2'. With
'trunk' versions 'release' is ignored and is automatically assigned
the current date.

This script uses 'setup.py' internally. Distribution packages are
created under 'dist' directory, which is first deleted.

Examples:
  python package.py all 2.0 final
  python package.py all 2.1.13 alpha
  python package.py sdist trunk
  python package.py version 2.0.1 alpha2
"""

import sys
import os
import shutil
import re
import time


ROOT = os.path.dirname(__file__)
DIST = os.path.join(ROOT, 'dist')
BUILD = os.path.join(ROOT, 'build')
SETUP = os.path.join(ROOT, 'setup.py')
VERSION = os.path.join(ROOT, 'src', 'robot', 'version.py')
VERSIONS = [re.compile('^2\.\d+(\.\d+)?$'), re.compile('^trunk$')]
RELEASES = [re.compile('^alpha\d*$'), re.compile('^beta\d*$'),
            re.compile('^rc\d*$'), re.compile('^final$')]


def sdist(*version_info):
    _clean()
    version(*version_info)
    _create_sdist()
    _announce()
    
def wininst(*version_info):
    _clean()
    version(*version_info)
    _create_wininst()
    _announce()

def all(*version_info):
    _clean()
    version(*version_info)
    _create_sdist()
    _create_wininst()
    _announce()

def version(version_number, release_tag=None):
    release_tag = _get_release_tag(version_number, release_tag)
    vfile = open(VERSION, 'w')
    vfile.write("VERSION = '%s'\n" % version_number)
    vfile.write("RELEASE = '%s'\n" % release_tag)
    vfile.write("TIMESTAMP = '%d%02d%02d-%02d%02d%02d'\n" % time.localtime()[:6])
    vfile.close()
    print "Updated version to %s %s" % (version_number, release_tag)
    
def _clean():
    print 'Cleaning up...'
    for path in [DIST, BUILD]:
        if os.path.exists(path):
            shutil.rmtree(path)

def _get_release_tag(version, tag):
    _verify_version(version, VERSIONS)
    if version == 'trunk':
        return '%d%02d%02d' % time.localtime()[:3]
    return _verify_version(tag, RELEASES)

def _verify_version(given, valid):
    for item in valid:
        if item.search(given):
            return given
    raise ValueError

def _create_sdist():
    _create('sdist', 'source distribution')

def _create_wininst():
    _create('bdist_wininst', 'Windows installer')

def _create(command, name):
    print 'Creating %s...' % name
    rc = os.system('%s %s %s' % (sys.executable, SETUP, command))
    if rc != 0:
        print 'Creating %s failed.' % name
        sys.exit(rc)
    print '%s created successfully.' % name.capitalize()

def _announce():
    print 'Created:'
    for path in os.listdir(DIST):
        print os.path.abspath(os.path.join(DIST, path))


if __name__ == '__main__':
    try:
        globals()[sys.argv[1]](*sys.argv[2:])
    except (KeyError, IndexError, TypeError, ValueError):
        print __doc__
