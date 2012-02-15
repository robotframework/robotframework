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

    def run_libdoc(self, args):
        cmd = self._cmd + [a for a in args.split(' ') if a]
        cmd[-1] = cmd[-1].replace('/', os.sep)
        logger.info(' '.join(cmd))
        stdout = tempfile.TemporaryFile()
        call(cmd, env=self._env, stdout=stdout, stderr=STDOUT, shell=os.sep=='\\')
        stdout.seek(0)
        output = stdout.read().replace('\r\n', '\n')
        logger.debug(output)
        return output
