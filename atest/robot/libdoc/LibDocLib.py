import json
import os
import pprint
import shlex
from os.path import abspath, dirname, exists, join, normpath, relpath
from subprocess import run, PIPE, STDOUT

from xmlschema import XMLSchema

from robot.api import logger
from robot.utils import CONSOLE_ENCODING, SYSTEM_ENCODING


ROOT = join(dirname(abspath(__file__)), '..', '..', '..')


class LibDocLib(object):

    def __init__(self, interpreter):
        self.libdoc = interpreter.libdoc
        self.encoding = SYSTEM_ENCODING \
            if not interpreter.is_ironpython else CONSOLE_ENCODING
        self.schema = XMLSchema(join(ROOT, 'doc', 'schema', 'libdoc.02.xsd'))

    def run_libdoc(self, args):
        cmd = self.libdoc + self._split_args(args)
        cmd[-1] = cmd[-1].replace('/', os.sep)
        logger.info(' '.join(cmd))
        result = run(cmd, cwd=join(ROOT, 'src'), stdout=PIPE, stderr=STDOUT,
                     encoding=self.encoding, timeout=120, universal_newlines=True)
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

    def validate_spec(self, path):
        self.schema.validate(path)

    def relative_source(self, path, start):
        if not exists(path):
            return path
        try:
            return relpath(path, start)
        except ValueError:
            return normpath(path)
