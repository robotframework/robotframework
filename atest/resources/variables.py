import os.path
import robot
import sys
import tempfile

__all__ = ['robotpath', 'javatempdir', 'robotversion']

robotpath = os.path.abspath(os.path.dirname(robot.__file__))
javatempdir = sys.platform == 'darwin' and '/tmp' or tempfile.gettempdir()
robotversion = robot.utils.get_version()
