import os
import tempfile
from os.path import join, dirname, abspath
from subprocess import call, STDOUT
from xml.etree import cElementTree as ET

from robot.api import logger

ROBOT_SRC = join(dirname(abspath(__file__)), '..', '..', '..', 'src')

class LibDocLib(object):

    def __init__(self, interpreter):
        self._interpreter = interpreter
        self._cmd = [interpreter, '-m', 'robot.libdoc']
        path_var = 'PYTHONPATH' if 'python' in interpreter else 'JYTHONPATH'
        self._env = os.environ.copy()
        self._env.update({path_var: ROBOT_SRC})
        self._last_output = ''

    def run_libdoc(self, options, library):
        options = options.split(' ') if options else []
        output = tempfile.TemporaryFile()
        cmd = self._cmd + options + [library.replace('/', os.sep)]
        logger.info(' '.join(cmd))
        rc = call(cmd, env=self._env, stdout=output,
                  stderr=STDOUT, shell=os.sep=='\\')
        output.seek(0)
        self._last_output = output.read()
        logger.debug(self._last_output)
        return rc

    def parse_libdoc_output(self, path=None):
        if path:
            return ET.parse(path).getroot()
        return ET.XML(self._last_output)
