#!/usr/bin/env python

import sys
import os
from distutils.core import setup

sys.path.insert(0, os.path.join('src','robot'))

from version import VERSION
import robot_postinstall


# Modes
INSTALL = 'install' in sys.argv
BDIST_WININST = 'bdist_wininst' in sys.argv or 'bdist' in sys.argv


def main():
    pkg_dir = 'src'
    scripts = [ os.path.join(pkg_dir,'bin',script) for script in
                ['pybot','jybot','rebot'] ]
    win_scripts = [ script+'.bat' for script in scripts ]
    all_scripts = scripts + win_scripts
    inst_pkgs = [ 'robot', 'robot.common', 'robot.conf', 'robot.libraries',
                  'robot.output', 'robot.parsing', 'robot.serializing',
                  'robot.running', 'robot.utils', 'robot.variables' ]
    if BDIST_WININST:
        inst_scripts = win_scripts
        inst_scripts.append('robot_postinstall.py') 
    else:
        inst_scripts = all_scripts

    # Let distutils take care of most of the setup
    dist = setup(
          name         = 'robotframework',
          version      = VERSION,
          description  = 'Robot -- Automating the h*ck out of it',
          author       = 'Robot Framework Developers',
          author_email = 'robotframework-devel@googlegroups.com',
          url          = 'http://robotframework.org',
          package_dir  = { '' : pkg_dir },
          packages     = inst_pkgs,
          scripts      = inst_scripts,
    )

    if INSTALL:
        def absnorm(path):
            # os.path.abspath does not normalize in Jython
            return os.path.abspath(os.path.normpath(path))
        
        script_dir = absnorm(dist.command_obj['install_scripts'].install_dir)
        module_dir = absnorm(dist.command_obj['install_lib'].install_dir)
        robot_dir = os.path.join(module_dir, 'robot')
        robot_postinstall.generic_install(script_dir, robot_dir)
    

if __name__ == "__main__":
    main()
