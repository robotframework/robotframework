"""Robot Framework post-install script for Windows.

This script is executed as the last part of the graphical Windows installation
and during un-installation started from `Add/Remote Programs`.

For more details:
http://docs.python.org/distutils/builtdist.html#postinstallation-script
"""

from os.path import join
import os
import sys


SCRIPT_DIR = join(sys.prefix, 'Scripts')
ROBOT_DIR = join(sys.prefix, 'Lib', 'site-packages', 'robot')
SUCCESS = '''Robot Framework installation was successful!

Add Python and Scripts directories to PATH to be able to use 'pybot'
and 'rebot' start-up scripts from the command line. Also add Jython
and IronPython installation directories to PATH to be able to use
'jybot' and 'ipybot' scripts, respectively.

Python directory: %s
Scripts directory: %s
''' % (sys.prefix, SCRIPT_DIR)


def windows_install():
    """Generates jybot.bat and ipybot.bat scripts."""
    try:
        _create_script('jybot.bat', 'jython')
        _create_script('ipybot.bat', 'ipy')
    except Exception as err:
        print 'Running post-install script failed: %s' % err
        print 'Robot Framework start-up scripts may not work correctly.'
        return
    # Avoid "close failed in file object destructor" error when UAC disabled
    # https://github.com/robotframework/robotframework/issues/1331
    if sys.stdout.fileno() != -2:
        print SUCCESS


def _create_script(name, interpreter):
    path = join(SCRIPT_DIR, name)
    runner = join(ROBOT_DIR, 'run.py')
    with open(path, 'w') as script:
        script.write('@echo off\n%s "%s" %%*\n' % (interpreter, runner))
    file_created(path)


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


if __name__ == '__main__':
    {'-install': windows_install,
     '-remove': windows_uninstall}[sys.argv[1]]()
