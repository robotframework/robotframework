#  Copyright 2008-2010 Nokia Siemens Networks Oyj
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

    def __init__(self, setting_name, parent=None, comment=None):
        self.setting_name = setting_name
        self.parent = parent
        self.comment = comment
        self.reset()

    def reset(self):
        self.value = []

    @property
    def source(self):
        return self.parent.source if self.parent else None

    @property
    def directory(self):
        return self.parent.directory if self.parent else None

    def populate(self, value, comment=None):
        """Mainly used at parsing time, later attributes can be set directly."""
        self._populate(value)
        self.comment = comment

    def _populate(self, value):
        self.value = value

    def is_set(self):
        return bool(self.value)

    def is_for_loop(self):
        return False

    def report_invalid_syntax(self, message, level='ERROR'):
        self.parent.report_invalid_syntax(message, level)

    def _string_value(self, value):
        return value if isinstance(value, basestring) else ' '.join(value)

    def _concat_string_with_value(self, string, value):
        if string:
            return string + ' ' + self._string_value(value)
        return self._string_value(value)

    def as_list(self):
        ret = self._data_as_list()
        if self.comment:
            ret.append('# %s' % self.comment)
        return ret

    def _data_as_list(self):
        ret = [self.setting_name]
        if self.value:
            ret.extend(self.value)
        return ret


class Documentation(_Setting):

    def reset(self):
        self.value = ''

    def _populate(self, value):
        self.value = self._concat_string_with_value(self.value, value)

    def _data_as_list(self):
        return [self.setting_name, self.value]


class Template(_Setting):

    def reset(self):
        self.value = None

    def _populate(self, value):
        self.value = self._concat_string_with_value(self.value, value)

    def is_set(self):
        return self.value is not None

    def _data_as_list(self):
        ret = [self.setting_name]
        if self.value:
            ret.append(self.value)
        return ret


class Fixture(_Setting):

    def reset(self):
        self.name = None
        self.args = []

    def _populate(self, value):
        if not self.name:
            self.name = value[0] if value else ''
            value = value[1:]
        self.args.extend(value)

    def is_set(self):
        return self.name is not None

    def _data_as_list(self):
        ret = [self.setting_name]
        if self.name or self.args:
            ret.append(self.name or '')
        if self.args:
            ret.extend(self.args)
        return ret


class Timeout(_Setting):

    def reset(self):
        self.value = None
        self.message = ''

    def _populate(self, value):
        if not self.value:
            self.value = value[0] if value else ''
            value = value[1:]
        self.message = self._concat_string_with_value(self.message, value)

    def is_set(self):
        return self.value is not None

    def _data_as_list(self):
        ret = [self.setting_name]
        if self.value or self.message:
            ret.append(self.value or '')
        if self.message:
            ret.append(self.message)
        return ret


class Tags(_Setting):

    def reset(self):
        self.value = None

    def _populate(self, value):
        self.value = (self.value or []) + value

    def is_set(self):
        return self.value is not None

    def __add__(self, other):
        if not isinstance(other, Tags):
            raise TypeError('Tags can only be added with tags')
        tags = Tags('Tags')
        tags.value = (self.value or []) + (other.value or [])
        return tags


class Arguments(_Setting):
    pass


class Return(_Setting):
    pass


class Metadata(_Setting):

    def __init__(self, setting_name, parent, name, value, comment=None):
        self.setting_name = setting_name
        self.parent = parent
        self.name = name
        self.value = self._string_value(value)
        self.comment = comment

    def is_set(self):
        return True

    def _data_as_list(self):
        return [self.setting_name, self.name, self.value]


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

    def _data_as_list(self):
        return [self.type, self.name] + self.args


class Library(_Import):

    def __init__(self, parent, name, args=None, alias=None, comment=None):
        if args and not alias:
            args, alias = self._split_alias(args)
        _Import.__init__(self, parent, name, args, alias, comment)

    def _split_alias(self, args):
        if len(args) >= 2 and args[-2].upper() == 'WITH NAME':
            return args[:-2], args[-1]
        return args, None

    def _data_as_list(self):
        alias = ['WITH NAME', self.alias] if self.alias else []
        return ['Library', self.name] + self.args + alias


class Resource(_Import):

    def __init__(self, parent, name, invalid_args=None, comment=None):
        if invalid_args:
            name += ' ' + ' '.join(invalid_args)
        _Import.__init__(self, parent, name, comment=comment)


class Variables(_Import):

    def __init__(self, parent, name, args=None, comment=None):
        _Import.__init__(self, parent, name, args, comment=comment)
