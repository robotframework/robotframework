#!/usr/bin/env python

"""Install script for Robot Framework source distributions.

Usage:  install.py [ in(stall) | un(install) | re(install) ]
"""

import sys
import os
import shutil


def install():
    cmd = '%s %s install' % (sys.executable, os.path.join(os.path.dirname(sys.argv[0]), 'setup.py'))
    print cmd
    rc = os.system(cmd)
    if rc != 0:
        print 'Installation failed'

def uninstall():
    try:
        inst_dir = _get_installation_directory()
    except:
        print 'Robot Framework is not installed or the installation is corrupted.'
        sys.exit(1)
    else:
        _remove(inst_dir)
        _remove_runners()

def reinstall():
    uninstall()
    install()

def _get_installation_directory():
    import robot
    # Ensure we got correct robot module
    if 'Robot' not in robot.pythonpathsetter.__doc__:
        raise ImportError
    return os.path.dirname(robot.__file__)

def _remove(path):
    if not os.path.exists(path):
        return
    print 'removing %s' %  path
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

def _remove_runners():
    for name in ['pybot', 'jybot', 'rebot']:
        if os.sep == '\\':
            _remove(os.path.join(sys.prefix, 'Scripts', name+'.bat'))
        else:
            for dirpath in ['/bin', '/usr/bin/', '/usr/local/bin' ]:
                 _remove(os.path.join(dirpath, name))


    


if __name__ == '__main__':
    actions = { 'install': install, 'in': install,
                'uninstall': uninstall, 'un': uninstall,
                'reinstall': reinstall, 're': reinstall }
    try:
        actions[sys.argv[1]]()
    except (KeyError, IndexError):
        print __doc__
    
