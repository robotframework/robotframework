import json
import os
import pprint
import shlex
from os.path import join, dirname, abspath
from subprocess import run, PIPE, STDOUT

from robot.api import logger
from robot.utils import CONSOLE_ENCODING, SYSTEM_ENCODING


ROBOT_SRC = join(dirname(abspath(__file__)), '..', '..', '..', 'src')


class LibDocLib(object):

    def __init__(self, interpreter):
        self._libdoc = interpreter.libdoc
        self._encoding = SYSTEM_ENCODING \
            if not interpreter.is_ironpython else CONSOLE_ENCODING

    def run_libdoc(self, args):
        cmd = self._libdoc + self._split_args(args)
        cmd[-1] = cmd[-1].replace('/', os.sep)
        logger.info(' '.join(cmd))
        result = run(cmd, cwd=ROBOT_SRC, stdout=PIPE, stderr=STDOUT,
                     encoding=self._encoding, universal_newlines=True)
        logger.info(result.stdout)
        return result.stdout

    def _split_args(self, args):
        lexer = shlex.shlex(args, posix=True)
        lexer.escape = ''
        lexer.whitespace_split = True
        return list(lexer)

    def get_libdoc_model_from_html(self, path):
        with open(path, encoding='UTF-8') as html_file:
            model_string = self._find_model(html_file)
        model = json.loads(model_string.replace('\\x3c/', '</'))
        logger.info(pprint.pformat(model))
        return model

    def _find_model(self, html_file):
        for line in html_file:
            if line.startswith('libdoc = '):
                return line.split('=', 1)[1].strip(' \n;')
        raise RuntimeError('No model found from HTML')
