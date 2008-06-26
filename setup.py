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

import sys
import os
from distutils.core import setup

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src','robot'))

from version import VERSION, RELEASE
import robot_postinstall


if RELEASE != 'final':
    VERSION += '-' + RELEASE
INSTALL = 'install' in sys.argv
WININST = 'bdist_wininst' in sys.argv

DESCRIPTION = """
Robot Framework is a Python-based keyword-driven test automation framework
for acceptance level testing and acceptance test-driven development (ATDD).
It has an easy-to-use tabular syntax for creating test cases and its testing
capabilities can be extended by test libraries implemented either with 
Python or Java.  Users can also create new keywords from existing ones using
the same simple syntax that is used for creating test cases.
"""[1:-1]

CLASSIFIERS = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Testing
"""[1:-1]


def main():
    scripts = [ os.path.join('src','bin',script) for script in
                ['pybot','jybot','rebot'] ]
    win_scripts = [ script+'.bat' for script in scripts ]
    all_scripts = scripts + win_scripts
    inst_pkgs = [ 'robot', 'robot.common', 'robot.conf', 'robot.libraries',
                  'robot.output', 'robot.parsing', 'robot.serializing',
                  'robot.running', 'robot.utils', 'robot.variables' ]
    if WININST:
        inst_scripts = win_scripts
        inst_scripts.append('robot_postinstall.py') 
    else:
        inst_scripts = all_scripts

    # Let distutils take care of most of the setup
    dist = setup(
          name         = 'robotframework',
          version      = VERSION,
          author       = 'Robot Framework Developers',
          author_email = 'robotframework-devel@googlegroups.com',
          url          = 'http://robotframework.org',
          license      = 'Apache License 2.0',
          description  = 'A keyword-driven acceptance test automation framework',
          long_description = DESCRIPTION,
          keywords     = 'acceptance test automation atdd',
          platforms    = 'any',
          download_url = 'http://robotframework.googlecode.com/files/robotframework-2.0.tar.gz', 
          classifiers  = CLASSIFIERS.splitlines(),
          package_dir  = {'': 'src'},
          packages     = inst_pkgs,
          scripts      = inst_scripts,
    )

    if INSTALL:
        def absnorm(path):
            return os.path.abspath(os.path.normpath(path))
        
        script_dir = absnorm(dist.command_obj['install_scripts'].install_dir)
        module_dir = absnorm(dist.command_obj['install_lib'].install_dir)
        robot_dir = os.path.join(module_dir, 'robot')
        robot_postinstall.generic_install(script_dir, robot_dir)
    

if __name__ == "__main__":
    main()
