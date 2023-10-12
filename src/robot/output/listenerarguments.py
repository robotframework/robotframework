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

from robot.model import BodyItem
from robot.utils import is_list_like, is_dict_like, is_string, safe_str


class ListenerArguments:

    def __init__(self, arguments):
        self._arguments = arguments
        self._version2 = None
        self._version3 = None

    def get_arguments(self, version):
        if version == 2:
            if self._version2 is None:
                self._version2 = self._get_version2_arguments(*self._arguments)
            return self._version2
        else:
            if self._version3 is None:
                self._version3 = self._get_version3_arguments(*self._arguments)
            return self._version3

    def _get_version2_arguments(self, *arguments):
        return arguments

    def _get_version3_arguments(self, *arguments):
        return arguments

    @classmethod
    def by_method_name(cls, name, arguments):
        Arguments = {'start_suite': StartSuiteArguments,
                     'end_suite': EndSuiteArguments,
                     'start_test': StartTestArguments,
                     'end_test': EndTestArguments,
                     'start_keyword': StartKeywordArguments,
                     'end_keyword': EndKeywordArguments,
                     'log_message': MessageArguments,
                     'message': MessageArguments}.get(name, ListenerArguments)
        return Arguments(arguments)


class MessageArguments(ListenerArguments):

    def _get_version2_arguments(self, msg):
        # Timestamp in our legacy format.
        timestamp = msg.timestamp.isoformat(' ', timespec='milliseconds').replace('-', '')
        attributes = {'timestamp': timestamp,
                      'message': msg.message,
                      'level': msg.level,
                      'html': 'yes' if msg.html else 'no'}
        return attributes,

    def _get_version3_arguments(self, msg):
        return msg,


class _ListenerArgumentsFromItem(ListenerArguments):
    _attribute_names = None

    def _get_version2_arguments(self, item):
        attributes = dict((name, self._get_attribute_value(item, name))
                          for name in self._attribute_names)
        attributes.update(self._get_extra_attributes(item))
        return self._get_name(item) or '', attributes

    def _get_name(self, item):
        return item.name

    def _get_attribute_value(self, item, name):
        value = getattr(item, name)
        if value is None:
            return ''
        return self._take_copy_of_mutable_value(value)

    def _take_copy_of_mutable_value(self, value):
        if is_dict_like(value):
            return dict(value)
        if is_list_like(value):
            return list(value)
        return value

    def _get_extra_attributes(self, item):
        return {}

    def _get_version3_arguments(self, item):
        return item.data, item.result


class StartSuiteArguments(_ListenerArgumentsFromItem):
    _attribute_names = ('id', 'doc', 'metadata', 'starttime')

    def _get_extra_attributes(self, suite):
        return {'longname': suite.full_name,
                'tests': [t.name for t in suite.tests],
                'suites': [s.name for s in suite.suites],
                'totaltests': suite.test_count,
                'source': str(suite.source or '')}


class EndSuiteArguments(StartSuiteArguments):
    _attribute_names = ('id', 'doc', 'metadata', 'starttime',
                        'endtime', 'elapsedtime', 'status', 'message')

    def _get_extra_attributes(self, suite):
        attrs = super()._get_extra_attributes(suite)
        attrs['statistics'] = suite.stat_message
        return attrs


class StartTestArguments(_ListenerArgumentsFromItem):
    _attribute_names = ('id', 'doc', 'tags', 'lineno', 'starttime')

    def _get_extra_attributes(self, test):
        return {'longname': test.full_name,
                'source': str(test.source or ''),
                'template': test.template or '',
                'originalname': test.data.name}


class EndTestArguments(StartTestArguments):
    _attribute_names = ('id', 'doc', 'tags', 'lineno', 'starttime',
                        'endtime', 'elapsedtime', 'status', 'message')


class StartKeywordArguments(_ListenerArgumentsFromItem):
    _attribute_names = ('doc', 'tags', 'lineno', 'type', 'status', 'starttime')
    _type_attributes = {
        BodyItem.FOR: ('variables', 'flavor', 'values'),
        BodyItem.IF: ('condition',),
        BodyItem.ELSE_IF: ('condition',),
        BodyItem.EXCEPT: ('patterns', 'pattern_type', 'variable'),
        BodyItem.WHILE: ('condition', 'limit', 'on_limit_message'),    # FIXME: Add 'on_limit'
        BodyItem.RETURN: ('values',),
    }
    _for_flavor_attributes = {
        'IN ENUMERATE': ('start',),
        'IN ZIP': ('mode', 'fill')
    }

    def _get_name(self, kw):
        return kw.full_name if kw.type in kw.KEYWORD_TYPES else kw._name

    def _get_extra_attributes(self, kw):
        # FOR and TRY model objects use `assign` starting from RF 7.0, but for
        # backwards compatibility reasons we pass them as `variable(s)`.
        if kw.type in kw.KEYWORD_TYPES:
            assign = list(kw.assign)
            name = kw.name or ''
            owner = kw.owner or ''
            args = [a if is_string(a) else safe_str(a) for a in kw.args]
        else:
            assign = []
            name = kw._name
            owner = ''
            args = []
        attrs = {'kwname': name,
                 'libname': owner,
                 'args': args,
                 'assign': assign,
                 'source': str(kw.source or '')}
        if kw.type in self._type_attributes:
            for name in self._type_attributes[kw.type]:
                # FOR and TRY model objects use `assign` instead of `variable(s)`
                # starting from RF 7.0, but we want to use old names with listeners.
                model_name = name if name not in ('variables', 'variable') else 'assign'
                if hasattr(kw, model_name):
                    attrs[name] = self._get_attribute_value(kw, model_name)
        elif kw.type == BodyItem.ITERATION and kw.parent.type == BodyItem.FOR:
            attrs['variables'] = dict(kw.assign)
        if kw.type == BodyItem.FOR:
            for name in self._for_flavor_attributes.get(kw.flavor, ()):
                attrs[name] = self._get_attribute_value(kw, name)
        return attrs


class EndKeywordArguments(StartKeywordArguments):
    _attribute_names = ('doc', 'assign', 'tags', 'lineno', 'type', 'status',
                        'starttime', 'endtime', 'elapsedtime')
