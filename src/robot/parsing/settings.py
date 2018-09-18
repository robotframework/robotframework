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

from robot.utils import is_string, py2to3, unicode

from .comments import Comment


@py2to3
class Setting(object):

    def __init__(self, setting_name, parent=None, comment=None):
        self.setting_name = setting_name
        self.parent = parent
        self._set_initial_value()
        self._set_comment(comment)
        self._populated = False

    def _set_initial_value(self):
        self.value = []

    def _set_comment(self, comment):
        self.comment = Comment(comment)

    def reset(self):
        self.__init__(self.setting_name, self.parent)

    @property
    def source(self):
        return self.parent.source if self.parent is not None else None

    @property
    def directory(self):
        return self.parent.directory if self.parent is not None else None

    def populate(self, value, comment=None):
        """Mainly used at parsing time, later attributes can be set directly."""
        if not self._populated:
            self._populate(value)
            self._set_comment(comment)
            self._populated = True
        else:
            self._set_initial_value()
            self._set_comment(None)
            self.report_invalid_syntax("Setting '%s' used multiple times."
                                       % self.setting_name, 'ERROR')

    def _populate(self, value):
        self.value = value

    def is_set(self):
        return bool(self.value)

    def is_for_loop(self):
        return False

    def report_invalid_syntax(self, message, level='ERROR'):
        self.parent.report_invalid_syntax(message, level)

    def _string_value(self, value):
        return value if is_string(value) else ' '.join(value)

    def _concat_string_with_value(self, string, value):
        if string:
            return string + ' ' + self._string_value(value)
        return self._string_value(value)

    def as_list(self):
        return self._data_as_list() + self.comment.as_list()

    def _data_as_list(self):
        ret = [self.setting_name]
        if self.value:
            ret.extend(self.value)
        return ret

    def __nonzero__(self):
        return self.is_set()

    def __iter__(self):
        return iter(self.value or ())

    def __unicode__(self):
        return unicode(self.value or '')


class StringValueJoiner(object):

    def __init__(self, separator):
        self._separator = separator

    def join_string_with_value(self, string, value):
        if string:
            return string + self._separator + self.string_value(value)
        return self.string_value(value)

    def string_value(self, value):
        if is_string(value):
            return value
        return self._separator.join(value)


class Documentation(Setting):

    def _set_initial_value(self):
        self.value = ''

    def _populate(self, value):
        self.value = self._concat_string_with_value(self.value, value)

    def _string_value(self, value):
        return value if is_string(value) else ''.join(value)

    def _data_as_list(self):
        return [self.setting_name, self.value]


class Template(Setting):

    def _set_initial_value(self):
        self.value = None

    def _populate(self, value):
        self.value = self._concat_string_with_value(self.value, value)

    def is_set(self):
        return self.value is not None

    def is_active(self):
        return self.value and self.value.upper() != 'NONE'

    def _data_as_list(self):
        ret = [self.setting_name]
        if self.value:
            ret.append(self.value)
        return ret


class Fixture(Setting):

    # `keyword`, `is_comment` and `assign` make the API compatible with Step.

    @property
    def keyword(self):
        return self.name or ''

    def is_comment(self):
        return False

    def _set_initial_value(self):
        self.name = None
        self.args = []
        self.assign = ()

    def _populate(self, value):
        if not self.name:
            self.name = value[0] if value else ''
            value = value[1:]
        self.args.extend(value)

    def is_set(self):
        return self.name is not None

    def is_active(self):
        return self.name and self.name.upper() != 'NONE'

    def _data_as_list(self):
        ret = [self.setting_name]
        if self.name or self.args:
            ret.append(self.name or '')
        if self.args:
            ret.extend(self.args)
        return ret


class Timeout(Setting):

    def _set_initial_value(self):
        self.value = None
        self.message = ''

    def _populate(self, value):
        if not self.value:
            self.value = value[0] if value else ''
            value = value[1:]
        self.message = self._concat_string_with_value(self.message, value)
        # TODO: Remove custom timeout message support in RF 3.2.
        if value and self.parent:
            self.parent.report_invalid_syntax(
                'Using custom timeout messages is deprecated since Robot '
                'Framework 3.0.1 and will be removed in future versions. '
                "Message that was used is '%s'." % self.message, level='WARN')

    def is_set(self):
        return self.value is not None

    def _data_as_list(self):
        ret = [self.setting_name]
        if self.value or self.message:
            ret.append(self.value or '')
        if self.message:
            ret.append(self.message)
        return ret


class Tags(Setting):

    def _set_initial_value(self):
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


class Arguments(Setting):
    pass


class Return(Setting):
    pass


class Metadata(Setting):
    setting_name = 'Metadata'

    def __init__(self, parent, name, value, comment=None, joined=False):
        self.parent = parent
        self.name = name
        joiner = StringValueJoiner('' if joined else ' ')
        self.value = joiner.join_string_with_value('', value)
        self._set_comment(comment)

    def reset(self):
        pass

    def is_set(self):
        return True

    def _data_as_list(self):
        return [self.setting_name, self.name, self.value]


class _Import(Setting):

    def __init__(self, parent, name, args=None, alias=None, comment=None):
        self.parent = parent
        self.name = name
        self.args = args or []
        self.alias = alias
        self._set_comment(comment)

    def reset(self):
        pass

    @property
    def type(self):
        return type(self).__name__

    def is_set(self):
        return True

    def _data_as_list(self):
        return [self.type, self.name] + self.args

    def report_invalid_syntax(self, message, level='ERROR', parent=None):
        parent = parent or getattr(self, 'parent', None)
        if parent:
            parent.report_invalid_syntax(message, level)
        else:
            from robot.api import logger
            logger.write(message, level)


class Library(_Import):

    def __init__(self, parent, name, args=None, alias=None, comment=None):
        if args and not alias:
            args, alias = self._split_possible_alias(args)
        _Import.__init__(self, parent, name, args, alias, comment)

    def _split_possible_alias(self, args):
        if len(args) > 1 and args[-2] == 'WITH NAME':
            return args[:-2], args[-1]
        return args, None

    def _data_as_list(self):
        data = ['Library', self.name] + self.args
        if self.alias:
            data += ['WITH NAME', self.alias]
        return data


class Resource(_Import):

    def __init__(self, parent, name, invalid_args=None, comment=None):
        if invalid_args:
            name += ' ' + ' '.join(invalid_args)
        _Import.__init__(self, parent, name, comment=comment)


class Variables(_Import):

    def __init__(self, parent, name, args=None, comment=None):
        _Import.__init__(self, parent, name, args, comment=comment)


class _DataList(object):

    def __init__(self, parent):
        self._parent = parent
        self.data = []

    def add(self, meta):
        self._add(meta)

    def _add(self, meta):
        self.data.append(meta)

    def _parse_name_and_value(self, value):
        name = value[0] if value else ''
        return name, value[1:]

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, item):
        self.data[index] = item

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return iter(self.data)


class ImportList(_DataList):

    def populate_library(self, data, comment):
        self._populate(Library, data, comment)

    def populate_resource(self, data, comment):
        self._populate(Resource, data, comment)

    def populate_variables(self, data, comment):
        self._populate(Variables, data, comment)

    def _populate(self, item_class, data, comment):
        name, value = self._parse_name_and_value(data)
        self._add(item_class(self._parent, name, value, comment=comment))


class MetadataList(_DataList):

    def populate(self, name, value, comment):
        self._add(Metadata(self._parent, name, value, comment, joined=True))
