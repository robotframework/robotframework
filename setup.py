#!/usr/bin/env python

import sys
import os
from distutils.core import setup

import robot_postinstall
execfile(os.path.join(os.path.dirname(__file__),'src','robot','version.py'))


# Maximum width in Windows installer seems to be 70 characters -------|
DESCRIPTION = """
Robot Framework is a generic test automation framework for acceptance
testing and acceptance test-driven development (ATDD). It has
easy-to-use tabular test data syntax and utilizes the keyword-driven
testing approach. Its testing capabilities can be extended by test
libraries implemented either with Python or Java, and users can create
new keywords from existing ones using the same syntax that is used for
creating test cases.
"""[1:-1]
CLASSIFIERS = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Software Development :: Testing
"""[1:-1]
PACKAGES = ['robot', 'robot.api', 'robot.common', 'robot.conf',
            'robot.libraries', 'robot.output', 'robot.parsing',
            'robot.result', 'robot.running', 'robot.utils',
            'robot.variables']
SCRIPT_NAMES = ['pybot', 'jybot', 'rebot']
if os.name == 'java':
    SCRIPT_NAMES.remove('pybot')


def main():
    inst_scripts = [ os.path.join('src','bin',name) for name in SCRIPT_NAMES ]
    if 'bdist_wininst' in sys.argv:
        inst_scripts = [ script+'.bat' for script in inst_scripts ]
        inst_scripts.append('robot_postinstall.py')
    elif os.sep == '\\':
        inst_scripts = [ script+'.bat' for script in inst_scripts ]

    if 'bdist_egg' in sys.argv:
        package_path = os.path.dirname(sys.argv[0])
        robot_postinstall.egg_preinstall(package_path, inst_scripts)

    # Let distutils take care of most of the setup
    dist = setup(
          name         = 'robotframework',
          version      = get_version(sep='-'),
          author       = 'Robot Framework Developers',
          author_email = 'robotframework-devel@googlegroups.com',
          url          = 'http://robotframework.org',
          license      = 'Apache License 2.0',
          description  = 'A generic test automation framework',
          long_description = DESCRIPTION,
          keywords     = 'robotframework testing testautomation atdd',
          platforms    = 'any',
          classifiers  = CLASSIFIERS.splitlines(),
          package_dir  = {'': 'src'},
          package_data = {'robot': ['webcontent/*.html', 'webcontent/*.css', 'webcontent/*.js', 'webcontent/lib/*.js']},
          packages     = PACKAGES,
          scripts      = inst_scripts,
    )

    if 'install' in sys.argv:
        absnorm = lambda path: os.path.abspath(os.path.normpath(path))
        script_dir = absnorm(dist.command_obj['install_scripts'].install_dir)
        module_dir = absnorm(dist.command_obj['install_lib'].install_dir)
        robot_dir = os.path.join(module_dir, 'robot')
        script_names = [ os.path.basename(name) for name in inst_scripts ]
        robot_postinstall.generic_install(script_names, script_dir, robot_dir)


if __name__ == "__main__":
    main()
