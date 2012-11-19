from os.path import abspath, dirname, join
import os
import robot

__all__ = ['ROBOTPATH', 'ROBOT_VERSION', 'DATADIR', 'WINDOWS']

ROBOTPATH = dirname(abspath(robot.__file__))
ROBOT_VERSION = robot.version.get_version()
DATADIR = join(dirname(abspath(__file__)), '..', 'testdata')
WINDOWS = os.sep == '\\'
