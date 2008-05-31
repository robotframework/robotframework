import time
import os.path
import robot

__all__ = ['timestamp', 'robotpath']

timetuple = time.localtime(time.time())[:6]  # from year to secs
timestamp = "%d%02d%02d-%02d%02d%02d" % timetuple
robotpath = os.path.abspath(os.path.dirname(robot.__file__))
