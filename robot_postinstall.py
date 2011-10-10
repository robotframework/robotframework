"""Robot Framework post-install script for Windows.

This script is executed as the last part of the graphical Windows installation
and during un-installation started from `Add/Remote Programs`.

For more details:
http://docs.python.org/distutils/builtdist.html#postinstallation-script
"""

from __future__ import with_statement
from os.path import join, isdir
import os
import sys


SCRIPT_DIR = join(sys.prefix, 'Scripts')
ROBOT_DIR = join(sys.prefix, 'Lib', 'site-packages', 'robot')
JYTHON = 'jython.bat'
IPY = 'ipy.exe'


def windows_install():
    """Generates jybot.bat and ipybot.bat scripts."""
    try:
        print 'Creating extra start-up scripts...'
        print 'Installation directory:', ROBOT_DIR
        _create_script(join(SCRIPT_DIR, 'jybot.bat'), JythonFinder().path)
        print '\nInstallation was successful. Happy Roboting!'
    except Exception, err:
        print '\nRunning post-install script failed: %s' % err
        print 'Robot Framework start-up scripts may not work correctly.'


def _create_script(path, interpreter):
    runner = join(ROBOT_DIR, 'runner.py')
    with open(path, 'w') as out:
        out.write('@echo off\n"%s" "%s" %%*\n' % (interpreter, runner))


def windows_uninstall():
    """Deletes Jython compiled files (*$py.class).

    Un-installer deletes files only if installer has created them and also
    deletes directories only if they are empty. Thus compiled files created
    by Jython must be deleted separately.
    """
    for base, _, files in os.walk(ROBOT_DIR):
        for name in files:
            if name.endswith('$py.class'):
                try:
                    os.remove(join(base, name))
                except OSError:
                    pass


class JythonFinder:
    """Tries to find path to Jython executable from system.

    First Jython is searched from PATH, then checked is JYTHON_HOME set, and
    finally Jython installation directory is searched from the system.
    """

    _excl_dirs = ['WINNT', 'RECYCLER']

    def __init__(self):
        self.path = self._find_jython()

    def _find_jython(self):
        if self._in_path(JYTHON):
            return JYTHON
        if self._is_jython_dir(os.environ.get('JYTHON_HOME')):
            return join(os.environ['JYTHON_HOME'], JYTHON)
        return self._search_jython_from_system() or JYTHON

    def _in_path(self, executable):
        with os.popen('%s --version 2>&1' % executable) as process:
            return process.read().startswith('Jython 2.5')

    def _is_jython_dir(self, path):
        if not path or not isdir(path):
            return False
        try:
            items = os.listdir(path)
        except OSError:
            return False
        return JYTHON in items and 'jython.jar' in items

    def _search_jython_from_systen(self):
        return self._search_jython_from_dirs(['C:\\', 'D:\\'])

    def _search_jython_from_dirs(self, paths, recursions=1):
        for path in paths:
            jython = self._search_jython_from_dir(path, recursions)
            if jython:
                return jython
        return None

    def _search_jython_from_dir(self, path, recursions):
        try:
            dirs = [join(path, name) for name in os.listdir(path)
                    if name not in self._excl_dirs and isdir(join(path, name))]
        except OSError:
            return None
        matches = [d for d in dirs if self._is_jython_dir(d)]
        if matches:
            # if multiple matches, the last one probably the latest version
            return os.path.join(path, matches[-1], JYTHON)
        if recursions:
            self._search_jyhon_from_dirs(dirs, recursions-1)
        return None


if __name__ == '__main__':
    {'-install': windows_install,
     '-remove': windows_uninstall}[sys.argv[1]]
