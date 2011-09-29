from os.path import abspath, dirname, join
import os
import tempfile
import robot

__all__ = ['ROBOTPATH', 'JAVATEMPDIR', 'ROBOT_VERSION', 'DATADIR', 'WINDOWS']

ROBOTPATH = dirname(abspath(robot.__file__))
JAVATEMPDIR = tempfile.gettempdir() # Used to be different on OSX and elsewhere
ROBOT_VERSION = robot.version.get_version()
DATADIR = join(dirname(abspath(__file__)), '..', 'testdata')
WINDOWS = os.sep == '\\'
