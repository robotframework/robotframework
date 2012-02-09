import os
import tempfile
from os.path import join, dirname, abspath
from subprocess import call, STDOUT

from robot.api import logger

ROBOT_SRC = join(dirname(abspath(__file__)), '..', '..', '..', 'src')

class LibDocLib(object):

    def __init__(self, interpreter):
        self._interpreter = interpreter
        self._cmd = [interpreter, '-m', 'robot.libdoc']
        path_var = 'PYTHONPATH' if 'python' in interpreter else 'JYTHONPATH'
        self._env = os.environ.copy()
        self._env.update({path_var: ROBOT_SRC})

    def run_libdoc(self, options, library):
        options = [o for o in options.split(' ') if o] if options else []
        stdout = tempfile.TemporaryFile()
        cmd = self._cmd + options + [library.replace('/', os.sep)]
        logger.info(' '.join(cmd))
        call(cmd, env=self._env, stdout=stdout, stderr=STDOUT, shell=os.sep=='\\')
        stdout.seek(0)
        output = stdout.read()
        logger.debug(output)
        return output
