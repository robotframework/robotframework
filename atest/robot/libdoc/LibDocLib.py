import json
import os
import pprint
import shlex
from pathlib import Path
from subprocess import run, PIPE, STDOUT

from jsonschema import Draft202012Validator
from xmlschema import XMLSchema

from robot.api import logger
from robot.utils import NOT_SET, SYSTEM_ENCODING
from robot.running.arguments import ArgInfo, TypeInfo


ROOT = Path(__file__).absolute().parent.parent.parent.parent


class LibDocLib:

    def __init__(self, interpreter=None):
        self.interpreter = interpreter
        self.xml_schema = XMLSchema(str(ROOT/'doc/schema/libdoc.xsd'))
        with open(ROOT/'doc/schema/libdoc.json') as f:
            self.json_schema = Draft202012Validator(json.load(f))

    @property
    def libdoc(self):
        return self.interpreter.libdoc

    def run_libdoc(self, args):
        cmd = self.libdoc + self._split_args(args)
        cmd[-1] = cmd[-1].replace('/', os.sep)
        logger.info(' '.join(cmd))
        result = run(cmd, cwd=ROOT/'src', stdout=PIPE, stderr=STDOUT,
                     encoding=SYSTEM_ENCODING, timeout=120, universal_newlines=True)
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
        model = json.loads(model_string)
        logger.info(pprint.pformat(model))
        return model

    def _find_model(self, html_file):
        for line in html_file:
            if line.startswith('libdoc = '):
                return line.split('=', 1)[1].strip(' \n;')
        raise RuntimeError('No model found from HTML')

    def validate_xml_spec(self, path):
        self.xml_schema.validate(path)

    def validate_json_spec(self, path):
        with open(path) as f:
            self.json_schema.validate(json.load(f))

    def get_repr_from_arg_model(self, model):
        return str(ArgInfo(kind=model['kind'],
                           name=model['name'],
                           type=self._get_type_info(model['type']),
                           default=self._get_default(model['default'])))

    def get_repr_from_json_arg_model(self, model):
        return str(ArgInfo(kind=model['kind'],
                           name=model['name'],
                           type=self._get_type_info(model['type']),
                           default=self._get_default(model['defaultValue'])))

    def _get_type_info(self, data):
        if not data:
            return None
        if isinstance(data, str):
            return TypeInfo.from_string(data)
        nested = [self._get_type_info(n) for n in data.get('nested', ())]
        return TypeInfo(data['name'], None, nested=nested or None)

    def _get_default(self, data):
        return data if data is not None else NOT_SET
