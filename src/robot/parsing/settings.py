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

    def __init__(self, parent=None, comment=None):
        self.parent = parent
        self.comment = comment
        self._init()

    def _init(self):
        self.value = []

    @property
    def source(self):
        return self.parent.source if self.parent else None

    @property
    def directory(self):
        return self.parent.directory if self.parent else None

    def set(self, value, comment=None):
        self._set(value)
        self.comment = comment

    def _set(self, value):
        self.value = value

    def is_set(self):
        return bool(self.value)

    def report_invalid_syntax(self, message, level='ERROR'):
        self.parent.report_invalid_syntax(message, level)

    def _string_value(self, value):
        return value if isinstance(value, basestring) else ' '.join(value)

    def _concat_string_with_value(self, str, value):
        str_val = self._string_value(value)
        str += str_val if not str else ' ' + str_val
        return str

class Documentation(_Setting):

    def _init(self):
        self.value = ''

    def _set(self, value):
        self.value = self._concat_string_with_value(self.value, value)


class Fixture(_Setting):

    def _init(self):
        self.name = None
        self.args = []

    def _set(self, value):
        if not self.name:
            self.name = value[0] if value else ''
            value = value[1:]
        self.args.extend(value)

    def is_set(self):
        return self.name is not None


class Timeout(_Setting):

    def _init(self):
        self.value = None
        self.message = ''

    def _set(self, value):
        if not self.value:
            self.value = value[0] if value else ''
            value = value[1:]
        self.message = self._concat_string_with_value(self.message, value)

    def is_set(self):
        return self.value is not None


class Tags(_Setting):

    def _init(self):
        self.value = []
        self._is_set = False

    def _set(self, value):
        self.value.extend(value)
        self._is_set = True

    def is_set(self):
        return self._is_set


class Arguments(_Setting):
    pass


class Return(_Setting):
    pass


class Metadata(_Setting):

    def __init__(self, parent, name, value, comment=None):
        self.parent = parent
        self.name = name
        self.value = self._string_value(value)
        self.comment = comment

    def is_set(self):
        return True


class _Import(_Setting):

    def __init__(self, parent, name, args=None, alias=None, comment=None):
        self.parent = parent
        self.name = name
        self.args = args or []
        self.alias = alias
        self.comment = comment

    @property
    def type(self):
        return type(self).__name__

    def is_set(self):
        return True


class Library(_Import):

    def __init__(self, parent, name, args=None, alias=None, comment=None):
        if args and not alias:
            args, alias = self._split_alias(args)
        _Import.__init__(self, parent, name, args, alias, comment)

    def _split_alias(self, args):
        if len(args) >= 2 and args[-2].upper() == 'WITH NAME':
            return args[:-2], args[-1]
        return args, None


class Resource(_Import):

    def __init__(self, parent, name, invalid_args=None, comment=None):
        if invalid_args:
            name += ' ' + ' '.join(invalid_args)
        _Import.__init__(self, parent, name, comment=comment)


class Variables(_Import):

    def __init__(self, parent, name, args=None, comment=None):
        _Import.__init__(self, parent, name, args, comment=comment)
