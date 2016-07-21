import json
import os
import pprint
import shlex
import tempfile
from os.path import join, dirname, abspath
from subprocess import call, STDOUT

from robot.api import logger
from robot.utils import console_decode

ROBOT_SRC = join(dirname(abspath(__file__)), '..', '..', '..', 'src')


class LibDocLib(object):

    def __init__(self, interpreter):
        self._libdoc = interpreter.libdoc
        self._encoding = 'CONSOLE' if interpreter.is_ironpython else 'SYSTEM'

    def run_libdoc(self, args):
        cmd = self._libdoc + self._split_args(args)
        cmd[-1] = cmd[-1].replace('/', os.sep)
        logger.info(' '.join(cmd))
        stdout = tempfile.TemporaryFile()
        call(cmd, cwd=ROBOT_SRC, stdout=stdout, stderr=STDOUT)
        stdout.seek(0)
        output = stdout.read().replace('\r\n', '\n')
        logger.info(output)
        return console_decode(output, encoding=self._encoding)

    def _split_args(self, args):
        lexer = shlex.shlex(args.encode('UTF-8'), posix=True)
        lexer.escape = ''
        lexer.whitespace_split = True
        return [token.decode('UTF-8') for token in lexer]

    def get_libdoc_model_from_html(self, path):
        with open(path) as html_file:
            model_string = self._find_model(html_file)
        model = json.loads(model_string.replace('\\x3c/', '</'))
        logger.info(pprint.pformat(model))
        return model

    def _find_model(self, html_file):
        for line in html_file:
            if line.startswith('libdoc = '):
                return line.split('=', 1)[1].strip(' \n;')
        raise RuntimeError('No model found from HTML')
