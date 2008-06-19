#!/usr/bin/env python

"""Install script for Robot Framework source distributions.

Usage:  install.py [ in(stall) | un(install) | re(install) ]

Using 'python install.py install' simply runs 'python setup.py install'
internally. You need to use 'setup.py' directly, if you want to alter the
default installation somehow.

See 'INSTALL.txt' or Robot Framework User Guide for more information.
"""

import sys
import os
import shutil


def install():
    print 'Ininstalling Robot Framework...'
    setup = os.path.join(os.path.dirname(sys.argv[0]), 'setup.py')
    rc = os.system('%s %s install' % (sys.executable, setup))
    if rc != 0:
        print 'Installation failed.'
        sys.exit(rc)
    print 'Installation successful.'

def uninstall():
    print 'Uninstalling Robot Framework...'
    try:
        instdir = _get_installation_directory()
    except Exception:
        print 'Robot Framework is not installed or the installation is corrupted.'
        sys.exit(1)
    _remove(instdir)
    _remove_runners()
    print 'Uninstallation successful.'

def reinstall():
    uninstall()
    install()


def _get_installation_directory():
    import robot
    # Ensure we got correct robot module
    if 'Robot' not in robot.pythonpathsetter.__doc__:
        raise TypeError
    return os.path.dirname(robot.__file__)

def _remove_runners():
    for name in ['pybot', 'jybot', 'rebot']:
        if os.sep == '\\':
            _remove(os.path.join(sys.prefix, 'Scripts', name+'.bat'))
        else:
            for dirpath in ['/bin', '/usr/bin/', '/usr/local/bin' ]:
                 _remove(os.path.join(dirpath, name))

def _remove(path):
    if not os.path.exists(path):
        return
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    except Exception, err:
        print "Removing '%s' failed: %s" % err
        sys.exit(1)
    else:
        print "Removed '%s'" % path


if __name__ == '__main__':
    actions = { 'install': install, 'in': install,
                'uninstall': uninstall, 'un': uninstall,
                'reinstall': reinstall, 're': reinstall }
    try:
        actions[sys.argv[1]]()
    except (KeyError, IndexError):
        print __doc__
