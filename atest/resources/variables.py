import time
import os.path
import robot
import sys
import tempfile

__all__ = ['timestamp', 'robotpath', 'javatempdir', 'robotversion']

timetuple = time.localtime(time.time())[:6]  # from year to secs
timestamp = "%d%02d%02d-%02d%02d%02d" % timetuple
robotpath = os.path.abspath(os.path.dirname(robot.__file__))
javatempdir = sys.platform == 'darwin' and '/tmp' or tempfile.gettempdir()
robotversion = robot.utils.get_version()