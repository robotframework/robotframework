#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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


import re

from robot import utils
from robot.errors import DataError
from robot.common import BaseKeyword
from robot.variables import is_var, is_scalar_var


def KeywordList(rawkeywords):
    keywords = []
    block = None
    for row in rawkeywords:
        if len(row) == 0:
            continue
        if block is not None and row[0] in ['', '\\']:
            block.add_row(row[1:])
        else:
            try:
                kw = block = BlockKeywordFactory(row)
            except TypeError:
                kw = KeywordFactory(row)
                block = None
            keywords.append(kw)
    return keywords


def KeywordFactory(kwdata):
    try:
        try:
            return SetKeyword(kwdata)
        except TypeError:
            pass
        try:
            return RepeatKeyword(kwdata)
        except TypeError:
            pass
    except:
        return SyntaxErrorKeyword(kwdata, utils.get_error_message())
    return BaseKeyword(kwdata[0], kwdata[1:])


def BlockKeywordFactory(data):
    if data[0].startswith(':'):
        name = utils.normalize(data[0].replace(':',''))
        try:
            if name == 'parallel':
                return ParallelKeyword(data[1:])
            if name == 'for':
                return ForKeyword(data[1:])
        except:
            return SyntaxErrorKeyword(data, utils.get_error_message())
    raise TypeError('Not BlockKeyword')


class SetKeyword(BaseKeyword):

    def __init__(self, kwdata):
        self.scalar_vars, self.list_var, name, args = self._process_data(kwdata)
        BaseKeyword.__init__(self, name, args, type='set')

    def _process_data(self, kwdata):
        scalar_vars, list_var = self._get_vars(kwdata)
        var_count = len(scalar_vars) + (list_var is not None and 1 or 0)
        if var_count == 0:
            raise TypeError('Not SetKeyword')
        try:
            name = kwdata[var_count]
            args = kwdata[var_count+1:]
        except IndexError:
            raise DataError('No keyword specified')
        return scalar_vars, list_var, name, args

    def _get_vars(self, data):
        scalar_vars = []
        list_var = None
        assign_mark_used = 'NO'
        for item in data:
            if item == '':
                break
            if item[-1] == '=':
                item = item[:-1].strip()
                if assign_mark_used == 'NO':
                    assign_mark_used = 'THIS ROUND'
            if not is_var(item):
                break
            if assign_mark_used == 'YES':
                raise DataError("Only the last variable can have '=' mark")
            if assign_mark_used == 'THIS ROUND':
                assign_mark_used = 'YES'
            if list_var is not None:
                raise DataError('Only the last variable can be a list variable')
            if is_scalar_var(item):
                scalar_vars.append(item)
            else:
                list_var = item
        return scalar_vars, list_var


class RepeatKeyword(BaseKeyword):

    _repeat_re = re.compile('^(.+)\s*[xX]$')

    def __init__(self, kwdata):
        self.repeat, name, args = self._process_data(kwdata)
        BaseKeyword.__init__(self, name, args, type='repeat')

    def _process_data(self, kwdata):
        res = self._repeat_re.search(kwdata[0])
        if res is None:
            raise TypeError('Not RepeatKeyword')
        repeat = res.group(1).strip()
        if not is_scalar_var(repeat):
            try:
                repeat = int(repeat)
            except ValueError:
                raise TypeError('Not RepeatKeyword')
        try:
            return repeat, kwdata[1], kwdata[2:]
        except IndexError:
            raise DataError('No keyword specified after the repeat count')


class _BlockKeyword(BaseKeyword):

    def add_row(self, data):
        if len(data) > 0:
            kw = KeywordFactory(data)
            self.keywords.append(kw)


class ForKeyword(_BlockKeyword):

    def __init__(self, params):
        self.vars, self.items, self.range = self._process_params(params)
        self.keywords = []
        name = '%s %s [ %s ]' % (' | '.join(self.vars),
                                 self.range and 'IN RANGE' or 'IN',
                                 ' | '.join(self.items))
        _BlockKeyword.__init__(self, name, type='for')

    def _process_params(self, params):
        in_index, range_ = self._get_in_index(params)
        vars = self._validate_vars(params[:in_index])
        items = params[in_index+1:]
        return vars, items, range_

    def _get_in_index(self, params):
        for index, item in enumerate(params):
            if utils.eq(item, 'IN'):
                return index, False
            if utils.eq(item, 'IN RANGE'):
                return index, True
        self._raise_invalid_syntax()

    def _validate_vars(self, vars):
        if len(vars) == 0:
            self._raise_invalid_syntax()
        for var in vars:
            if not is_scalar_var(var):
                self._raise_invalid_syntax()
        return vars

    def _raise_invalid_syntax(self):
        raise DataError('Invalid syntax in FOR loop. Expected format:\n'
                        '| : FOR | ${var} | IN | item1 | item2 |')


class ParallelKeyword(_BlockKeyword):

    def __init__(self, first_row):
        _BlockKeyword.__init__(self, type='parallel')
        self.keywords = []
        self.add_row(first_row)


class SyntaxErrorKeyword(BaseKeyword):

    def __init__(self, kwdata, error):
        name = ' '.join(kwdata)
        BaseKeyword.__init__(self, name, type='error')
        self.error = 'Syntax error: ' + error

    def add_row(self, row):
        # Can be used also as a syntax errored block keyword
        pass
