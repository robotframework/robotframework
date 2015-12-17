#  Copyright 2008-2015 Nokia Solutions and Networks
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

from robot.utils import is_list_like, is_dict_like


class ListenerArguments(object):

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
        attributes = {'timestamp': msg.timestamp,
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
        return item.name, attributes

    def _get_attribute_value(self, item, name):
        value = getattr(item, name)
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
    _attribute_names = ('id', 'longname', 'doc', 'metadata', 'starttime')

    def _get_extra_attributes(self, suite):
        return {'tests': [t.name for t in suite.tests],
                'suites': [s.name for s in suite.suites],
                'totaltests': suite.test_count,
                'source': suite.source or ''}


class EndSuiteArguments(StartSuiteArguments):
    _attribute_names = ('id', 'longname', 'doc', 'metadata', 'starttime',
                        'endtime', 'elapsedtime', 'status', 'message')

    def _get_extra_attributes(self, suite):
        attrs = StartSuiteArguments._get_extra_attributes(self, suite)
        attrs['statistics'] = suite.stat_message
        return attrs


class StartTestArguments(_ListenerArgumentsFromItem):
    _attribute_names = ('id', 'longname', 'doc', 'tags', 'starttime')

    def _get_extra_attributes(self, test):
        return {'critical': 'yes' if test.critical else 'no',
                'template': test.template or ''}


class EndTestArguments(StartTestArguments):
    _attribute_names = ('id', 'longname', 'doc', 'tags', 'starttime',
                        'endtime', 'elapsedtime', 'status', 'message')


class StartKeywordArguments(_ListenerArgumentsFromItem):
    _attribute_names = ('kwname', 'libname', 'doc', 'args', 'assign', 'tags',
                        'starttime')
    _types = {'kw': 'Keyword', 'setup': 'Setup', 'teardown': 'Teardown',
              'for': 'For', 'foritem': 'For Item'}

    def _get_extra_attributes(self, kw):
        return {'type': self._types[kw.type]}


class EndKeywordArguments(StartKeywordArguments):
    _attribute_names = ('kwname', 'libname', 'doc', 'args', 'assign', 'tags',
                        'starttime', 'endtime', 'elapsedtime', 'status')
