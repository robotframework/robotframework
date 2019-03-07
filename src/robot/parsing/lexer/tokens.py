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


class Token(object):
    SETTING_HEADER = 'SETTING_HEADER'
    VARIABLE_HEADER = 'VARIABLE_HEADER'
    TESTCASE_HEADER = 'TESTCASE_HEADER'
    KEYWORD_HEADER = 'KEYWORD_HEADER'
    COMMENT_HEADER = 'COMMENT_HEADER'

    DOCUMENTATION = 'DOCUMENTATION'
    SUITE_SETUP = 'SUITE_SETUP'
    SUITE_TEARDOWN = 'SUITE_TEARDOWN'
    METADATA = 'METADATA'
    TEST_SETUP = 'TEST_SETUP'
    TEST_TEARDOWN = 'TEST_TEARDOWN'
    TEST_TEMPLATE = 'TEST_TEMPLATE'
    TEST_TIMEOUT = 'TEST_TIMEOUT'
    FORCE_TAGS = 'FORCE_TAGS'
    DEFAULT_TAGS = 'DEFAULT_TAGS'
    LIBRARY = 'LIBRARY'
    RESOURCE = 'RESOURCE'
    VARIABLES = 'VARIABLES'
    SETUP = 'SETUP'
    TEARDOWN = 'TEARDOWN'
    TEMPLATE = 'TEMPLATE'
    TIMEOUT = 'TIMEOUT'
    TAGS = 'TAGS'
    ARGUMENTS = 'ARGUMENTS'
    RETURN = 'RETURN'

    VARIABLE = 'VARIABLE'
    ARGUMENT = 'ARGUMENT'
    NAME = 'NAME'
    ASSIGN = 'ASSIGN'
    KEYWORD = 'KEYWORD'
    FOR = 'FOR'
    FOR_SEPARATOR = 'FOR_SEPARATOR'
    OLD_FOR_INDENT = 'OLD_FOR_INDENT'
    END = 'END'

    SEPARATOR = 'SEPARATOR'
    COMMENT = 'COMMENT'
    CONTINUATION = 'CONTINUATION'
    IGNORE = 'IGNORE'
    EOS = 'EOS'
    ERROR = 'ERROR'
    DATA = 'DATA'

    NON_DATA_TOKENS = {SEPARATOR, COMMENT, CONTINUATION, IGNORE}

    # TODO: Enable slots when we know what attributes ply needs.
    #__slots__ = ['type', 'value', 'lineno', 'columnno']

    def __init__(self, type, value='', lineno=-1, columnno=-1):
        self.type = type
        self.value = value
        self.lineno = lineno
        self.columnno = columnno

    def __str__(self):
        # TODO: __unicode__
        return self.value

    def __repr__(self):
        return 'Token(%s, %r, %s, %s)' % (self.type, self.value,
                                          self.lineno, self.columnno)


Token.DATA_TOKENS = [t for t in Token.__dict__
                     if t[0] != '_' and t not in Token.NON_DATA_TOKENS]


class EOS(Token):

    def __init__(self, lineno=-1, columnno=-1):
        Token.__init__(self, Token.EOS, '', lineno, columnno)

    @classmethod
    def from_token(cls, token):
        return EOS(token.lineno, token.columnno + len(token.value))
