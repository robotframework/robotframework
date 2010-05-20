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


class _Setting(object):

    def __init__(self, table=None, comment=None):
        self.table = table
        self.comment = comment
        self._init()

    def _init(self):
        self.value = []

    def set(self, value, comment=None):
        self._set(value)
        self.comment = comment

    def _set(self, value):
        self.value = value

    def _string_value(self, value):
        return value if isinstance(value, basestring) else ' '.join(value)


class Documentation(_Setting):

    def _init(self):
        self.value = ''

    def _set(self, value):
        self.value = self._string_value(value)


class Fixture(_Setting):

    def _init(self):
        self.name = None
        self.args = []

    def _set(self, value):
        self.name = value[0] if value else ''
        self.args = value[1:]


class Timeout(_Setting):

    def _init(self):
        self.value = None
        self.message = ''

    def _set(self, value):
        self.value = value[0] if value else ''
        self.message = ' '.join(value[1:])


class Tags(_Setting):
    pass


class Arguments(_Setting):
    pass


class Return(_Setting):
    pass


class Metadata(_Setting):

    def __init__(self, table, name, value, comment):
        self.table = table
        self.name = name
        self.value = self._string_value(value)
        self.comment = comment


class _Import(_Setting):

    def __init__(self, table, name, args=None, alias=None, comment=None):
        self.table = table
        self.name = name
        self.args = args or []
        self.alias = alias
        self.comment = comment

    @property
    def type(self):
        return type(self).__name__


class Library(_Import):

    def __init__(self, table, name, args=None, alias=None, comment=None):
        if args and not alias:
            args, alias = self._split_alias(args)
        _Import.__init__(self, table, name, args, alias, comment)

    def _split_alias(self, args):
        if len(args) >= 2 and args[-2].upper() == 'WITH NAME':
            return args[:-2], args[-1]
        return args, None


class Resource(_Import):

    def __init__(self, table, name, invalid_args=None, comment=None):
        if invalid_args:
            name += ' ' + ' '.join(invalid_args)
        _Import.__init__(self, table, name, comment=comment)


class Variables(_Import):

    def __init__(self, table, name, args=None, comment=None):
        _Import.__init__(self, table, name, args, comment=comment)
