#  Copyright 2008-2014 Nokia Solutions and Networks
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

import inspect
import os.path

from robot import utils
from robot.errors import DataError
from robot.model import Tags

from .loggerhelper import AbstractLoggerProxy
from .logger import LOGGER

if utils.is_jython:
    from java.lang import Object
    from java.util import HashMap


class _RecursionAvoidingMetaclass(type):
    """Metaclass to wrap listener methods so that they cannot cause recursion.

    Recursion would otherwise happen if one listener logs something and that
    message is received and logged again by log_message or message method.
    """

    def __new__(cls, name, bases, dct):
        for attr, value in dct.items():
            if not attr.startswith('_') and inspect.isroutine(value):
                dct[attr] = cls._wrap_listener_method(value)
        dct['_calling_method'] = False
        return type.__new__(cls, name, bases, dct)

    @staticmethod
    def _wrap_listener_method(method):
        def wrapped(self, *args):
            if not self._calling_method:
                self._calling_method = True
                method(self, *args)
                self._calling_method = False
        return wrapped


class Listeners(object):
    __metaclass__ = _RecursionAvoidingMetaclass
    _start_attrs = ('id', 'doc', 'starttime', 'longname')
    _end_attrs = _start_attrs + ('endtime', 'elapsedtime', 'status', 'message')
    _kw_extra_attrs = ('args', '-id', '-longname', '-message')

    def __init__(self, listeners):
        self._listeners = self._import_listeners(listeners)
        self._running_test = False
        self._setup_or_teardown_type = None

    def __nonzero__(self):
        return bool(self._listeners)

    def _import_listeners(self, listener_data):
        listeners = []
        for name, args in listener_data:
            try:
                listeners.append(ListenerProxy(name, args))
            except DataError, err:
                if args:
                    name += ':' + ':'.join(args)
                LOGGER.error("Taking listener '%s' into use failed: %s"
                             % (name, unicode(err)))
        return listeners

    def start_suite(self, suite):
        for listener in self._listeners:
            if listener.version == 1:
                listener.call_method(listener.start_suite, suite.name, suite.doc)
            else:
                attrs = self._get_start_attrs(suite, 'metadata')
                attrs.update(self._get_suite_attrs(suite))
                listener.call_method(listener.start_suite, suite.name, attrs)

    def _get_suite_attrs(self, suite):
        return {
            'tests' : [t.name for t in suite.tests],
            'suites': [s.name for s in suite.suites],
            'totaltests': suite.test_count,
            'source': suite.source or ''
        }

    def end_suite(self, suite):
        for listener in self._listeners:
            self._notify_end_suite(listener, suite)

    def _notify_end_suite(self, listener, suite):
        if listener.version == 1:
            listener.call_method(listener.end_suite, suite.status,
                           suite.full_message)
        else:
            attrs = self._get_end_attrs(suite, 'metadata')
            attrs['statistics'] = suite.stat_message
            attrs.update(self._get_suite_attrs(suite))
            listener.call_method(listener.end_suite, suite.name, attrs)

    def start_test(self, test):
        self._running_test = True
        for listener in self._listeners:
            if listener.version == 1:
                listener.call_method(listener.start_test, test.name, test.doc,
                                     list(test.tags))
            else:
                attrs = self._get_start_attrs(test, 'tags')
                attrs['critical'] = 'yes' if test.critical else 'no'
                attrs['template'] = test.template or ''
                listener.call_method(listener.start_test, test.name, attrs)

    def end_test(self, test):
        self._running_test = False
        for listener in self._listeners:
            self._notify_end_test(listener, test)

    def _notify_end_test(self, listener, test):
        if listener.version == 1:
            listener.call_method(listener.end_test, test.status, test.message)
        else:
            attrs = self._get_end_attrs(test, 'tags')
            attrs['critical'] = 'yes' if test.critical else 'no'
            attrs['template'] = test.template or ''
            listener.call_method(listener.end_test, test.name, attrs)

    def start_keyword(self, kw):
        for listener in self._listeners:
            if listener.version == 1:
                listener.call_method(listener.start_keyword, kw.name, kw.args)
            else:
                attrs = self._get_start_attrs(kw, *self._kw_extra_attrs)
                attrs['type'] = self._get_keyword_type(kw, start=True)
                listener.call_method(listener.start_keyword, kw.name, attrs)

    def end_keyword(self, kw):
        for listener in self._listeners:
            if listener.version == 1:
                listener.call_method(listener.end_keyword, kw.status)
            else:
                attrs = self._get_end_attrs(kw, *self._kw_extra_attrs)
                attrs['type'] = self._get_keyword_type(kw, start=False)
                listener.call_method(listener.end_keyword, kw.name, attrs)

    def _get_keyword_type(self, kw, start=True):
        # When running setup or teardown, only the top level keyword has type
        # set to setup/teardown but we want to pass that type also to all
        # start/end_keyword listener methods called below that keyword.
        if kw.type == 'kw':
            return self._setup_or_teardown_type or 'Keyword'
        kw_type = self._get_setup_or_teardown_type(kw)
        self._setup_or_teardown_type = kw_type if start else None
        return kw_type

    def _get_setup_or_teardown_type(self, kw):
        return '%s %s' % (('Test' if self._running_test else 'Suite'),
                          kw.type.title())

    def log_message(self, msg):
        for listener in self._listeners:
            if listener.version == 2:
                listener.call_method(listener.log_message, self._create_msg_dict(msg))

    def message(self, msg):
        for listener in self._listeners:
            if listener.version == 2:
                listener.call_method(listener.message, self._create_msg_dict(msg))

    def _create_msg_dict(self, msg):
        return {'timestamp': msg.timestamp, 'message': msg.message,
                'level': msg.level, 'html': 'yes' if msg.html else 'no'}

    def output_file(self, name, path):
        for listener in self._listeners:
            listener.call_method(getattr(listener, '%s_file' % name.lower()), path)

    def close(self):
        for listener in self._listeners:
            listener.call_method(listener.close)

    def _get_start_attrs(self, item, *extra):
        return self._get_attrs(item, self._start_attrs, extra)

    def _get_end_attrs(self, item, *extra):
        return self._get_attrs(item, self._end_attrs, extra)

    def _get_attrs(self, item, default, extra):
        names = self._get_attr_names(default, extra)
        return dict((n, self._get_attr_value(item, n)) for n in names)

    def _get_attr_names(self, default, extra):
        names = list(default)
        for name in extra:
            if not name.startswith('-'):
                names.append(name)
            elif name[1:] in names:
                names.remove(name[1:])
        return names

    def _get_attr_value(self, item, name):
        value = getattr(item, name)
        return self._take_copy_of_mutable_value(value)

    def _take_copy_of_mutable_value(self, value):
        if isinstance(value, (dict, utils.NormalizedDict)):
            return dict(value)
        if isinstance(value, (list, tuple, Tags)):
            return list(value)
        return value


class ListenerProxy(AbstractLoggerProxy):
    _methods = ['start_suite', 'end_suite', 'start_test', 'end_test',
                'start_keyword', 'end_keyword', 'log_message', 'message',
                'output_file', 'report_file', 'log_file', 'debug_file',
                'xunit_file', 'close']

    def __init__(self, name, args):
        listener = self._import_listener(name, args)
        AbstractLoggerProxy.__init__(self, listener)
        self.name = name
        self.version = self._get_version(listener)
        self.is_java = self._is_java(listener)

    def _is_java(self, listener):
        return utils.is_jython and isinstance(listener, Object)

    def _import_listener(self, name, args):
        importer = utils.Importer('listener')
        return importer.import_class_or_module(os.path.normpath(name),
                                               instantiate_with_args=args)

    def _get_version(self, listener):
        try:
            return int(getattr(listener, 'ROBOT_LISTENER_API_VERSION', 1))
        except ValueError:
            return 1

    def call_method(self, method, *args):
        if self.is_java:
            args = [self._to_map(a) if isinstance(a, dict) else a for a in args]
        try:
            method(*args)
        except:
            message, details = utils.get_error_details()
            LOGGER.error("Calling listener method '%s' of listener '%s' failed: %s"
                     % (method.__name__, self.name, message))
            LOGGER.info("Details:\n%s" % details)

    def _to_map(self, dictionary):
        map = HashMap()
        for key, value in dictionary.iteritems():
            map.put(key, value)
        return map


# TODO: Remove in 2.9, left here in 2.8.5 for backwards compatibility.
# Consider also decoupling importing from __init__ to ease extending.
_ListenerProxy = ListenerProxy
