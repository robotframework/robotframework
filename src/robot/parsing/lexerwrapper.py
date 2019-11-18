#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os.path

from robot.errors import DataError
from robot.output import LOGGER
from robot.utils import Utf8Reader, get_error_message

from .restreader import read_rest


PROCESS_CURDIR = True


# TODO: Better name, maybe needs a public API?
class LexerWrapper(object):

    def __init__(self, lexer, source):
        self.source = source
        self.curdir = os.path.dirname(source).replace('\\', '\\\\')
        lexer.input(self._read(source))
        self.tokens = lexer.get_tokens()

    def _read(self, path):
        try:
            # IronPython handles BOM incorrectly if not using binary mode:
            # https://ironpython.codeplex.com/workitem/34655
            with open(path, 'rb') as data:
                if os.path.splitext(path)[1].lower() in ('.rest', '.rst'):
                    return read_rest(data)
                return Utf8Reader(data).read()
        except:
            raise DataError(get_error_message())

    def token(self):
        """Adapter for yacc.yacc"""
        token = next(self.tokens, None)
        if token and token.type == token.ERROR:
            self._report_error(token)
            return self._next_token_after_eos()
        if token and '${CURDIR}' in token.value and PROCESS_CURDIR:
            token.value = token.value.replace('${CURDIR}', self.curdir)
        return token

    def _report_error(self, token):
        # TODO: add line number
        LOGGER.error("Error in file '%s': %s" % (self.source, token.error))

    def _next_token_after_eos(self):
        while True:
            token = self.token()
            if token is None:
                return None
            if token.type == token.EOS:
                return self.token()
