#!/usr/bin/env python

"""Custom Robot Framework installation script.

Usage:  python install.py [ in(stall) | un(install) | re(install) ]

Using `python install.py install` simply runs `python setup.py install`
internally. You need to use `setup.py` directly, if you want to alter the
default installation somehow.

To install with with Jython or IronPython instead of Python, replace `python`
with `jython` or `ipy`, respectively.

For more information about installation in general see
http://code.google.com/p/robotframework/wiki/Installation
"""

import glob
import os
import shutil
import sys


def install():
    _remove(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'build'))
    print 'Installing Robot Framework...'
    setup = os.path.join(os.path.dirname(sys.argv[0]), 'setup.py')
    rc = os.system('"%s" %s install' % (sys.executable, setup))
    if rc != 0:
        print 'Installation failed.'
        sys.exit(rc)
    print 'Installation was successful.'

def uninstall():
    print 'Uninstalling Robot Framework...'
    try:
        instdir = _get_installation_directory()
    except Exception:
        print 'Robot Framework is not installed or the installation is corrupted.'
        sys.exit(1)
    _remove(instdir)
    if not 'robotframework' in instdir:
        _remove_egg_info(instdir)
    _remove_runners()
    print 'Uninstallation was successful.'

def reinstall():
    uninstall()
    install()


def _get_installation_directory():
    import robot
    # Ensure we got correct robot module
    if 'Robot' not in robot.pythonpathsetter.__doc__:
        raise TypeError
    robot_dir = os.path.dirname(robot.__file__)
    parent_dir = os.path.dirname(robot_dir)
    if 'robotframework' in os.path.basename(parent_dir):
        return parent_dir
    return robot_dir

def _remove_runners():
    runners = ['pybot', 'jybot', 'ipybot', 'rebot', 'jyrebot', 'ipyrebot']
    if os.sep == '\\':
        runners = [r + '.bat' for r in runners]
    for name in runners:
        if os.name == 'java':
            _remove(os.path.join(sys.prefix, 'bin', name))
        elif os.sep == '\\':
            _remove(os.path.join(sys.prefix, 'Scripts', name))
        else:
            for dirpath in ['/bin', '/usr/bin/', '/usr/local/bin']:
                 _remove(os.path.join(dirpath, name))

def _remove_egg_info(instdir):
    pattern = os.path.join(os.path.dirname(instdir), 'robotframework-*.egg-info')
    for path in glob.glob(pattern):
        _remove(path)

def _remove(path):
    if not os.path.exists(path):
        return
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
    except Exception, err:
        print "Removing '%s' failed: %s" % (path, err)
    else:
        print "Removed '%s'" % path


if __name__ == '__main__':
    actions = {'install': install, 'in': install,
               'uninstall': uninstall, 'un': uninstall,
               'reinstall': reinstall, 're': reinstall}
    try:
        actions[sys.argv[1]]()
    except (KeyError, IndexError):
        print __doc__
