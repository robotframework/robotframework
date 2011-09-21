from os.path import abspath, dirname, join
import tempfile
import robot

__all__ = ['robotpath', 'javatempdir', 'robotversion']

robotpath = abspath(dirname(robot.__file__))
javatempdir = tempfile.gettempdir() # Used to be different on OSX and elsewhere
robotversion = robot.version.get_version()
datadir = join(dirname(__file__), '..', 'testdata')
