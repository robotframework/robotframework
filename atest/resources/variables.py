import os.path
import robot
import sys
import tempfile

__all__ = ['robotpath', 'javatempdir', 'robotversion']

robotpath = os.path.abspath(os.path.dirname(robot.__file__))
javatempdir = tempfile.gettempdir() # Used to be different on OSX and elsewhere
robotversion = robot.utils.get_version()
