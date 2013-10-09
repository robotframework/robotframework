import json
import os
import pprint
import tempfile
from os.path import join, dirname, abspath
from subprocess import call, STDOUT

from robot.api import logger
from robot.utils import decode_output

ROBOT_SRC = join(dirname(abspath(__file__)), '..', '..', '..', 'src')

class LibDocLib(object):

    def __init__(self, interpreter):
        self._interpreter = interpreter
        self._cmd = [interpreter, '-m', 'robot.libdoc']

    def run_libdoc(self, args):
        cmd = self._cmd + [a for a in args.split(' ') if a]
        cmd[-1] = cmd[-1].replace('/', os.sep)
        logger.info(' '.join(cmd))
        # In Python 3, explicitly open in text mode (w+, default w+b)
        # causes less problems (works with str, not bytes):
        stdout = tempfile.TemporaryFile('w+')
        call(cmd, cwd=ROBOT_SRC, stdout=stdout, stderr=STDOUT, shell=os.sep=='\\')
        stdout.seek(0)
        output = stdout.read().replace('\r\n', '\n')
        logger.info(output)
        # Python 3 compatibility is handled by robot.utils.unic:
        return decode_output(output)

    def get_libdoc_model_from_html(self, path):
        with open(path) as html_file:
            model_string = self._find_model(html_file)
        model = json.loads(model_string)
        logger.info(pprint.pformat(model))
        return model

    def _find_model(self, html_file):
        for line in html_file:
            if line.startswith('libdoc = '):
                return line.split('=', 1)[1].strip(' \n;')
        raise RuntimeError('No model found from HTML')
