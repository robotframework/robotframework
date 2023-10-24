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

from robot.errors import DataError, TimeoutError
from robot.model import BodyItem
from robot.utils import (Importer, get_error_details, is_string, safe_str,
                         split_args_from_name_or_path, type_name)

from .loggerapi import LoggerApi
from .loggerhelper import IsLogged
from .logger import LOGGER


class Listeners(LoggerApi):

    def __init__(self, listeners, log_level='INFO'):
        self._is_logged = IsLogged(log_level)
        self.listeners = import_listeners(listeners)

    def start_suite(self, data: 'running.TestSuite', result: 'result.TestSuite'):
        for listener in self.listeners:
            listener.start_suite(data, result)

    def end_suite(self, data: 'running.TestSuite', result: 'result.TestSuite'):
        for listener in self.listeners:
            listener.end_suite(data, result)

    def start_test(self, data: 'running.TestCase', result: 'result.TestCase'):
        for listener in self.listeners:
            listener.start_test(data, result)

    def end_test(self, data: 'running.TestCase', result: 'result.TestCase'):
        for listener in self.listeners:
            listener.end_test(data, result)

    def start_keyword(self, data: 'running.Keyword', result: 'result.Keyword'):
        for listener in self.listeners:
            listener.start_keyword(data, result)

    def end_keyword(self, data: 'running.Keyword', result: 'result.Keyword'):
        for listener in self.listeners:
            listener.end_keyword(data, result)

    def start_for(self, data: 'running.For', result: 'result.For'):
        for listener in self.listeners:
            listener.start_for(data, result)

    def end_for(self, data: 'running.For', result: 'result.For'):
        for listener in self.listeners:
            listener.end_for(data, result)

    def start_for_iteration(self, data: 'running.For', result: 'result.ForIteration'):
        for listener in self.listeners:
            listener.start_for_iteration(data, result)

    def end_for_iteration(self, data: 'running.For', result: 'result.ForIteration'):
        for listener in self.listeners:
            listener.end_for_iteration(data, result)

    def start_while(self, data: 'running.While', result: 'result.While'):
        for listener in self.listeners:
            listener.start_while(data, result)

    def end_while(self, data: 'running.While', result: 'result.While'):
        for listener in self.listeners:
            listener.end_while(data, result)

    def start_while_iteration(self, data: 'running.While', result: 'result.WhileIteration'):
        for listener in self.listeners:
            listener.start_while_iteration(data, result)

    def end_while_iteration(self, data: 'running.While', result: 'result.WhileIteration'):
        for listener in self.listeners:
            listener.end_while_iteration(data, result)

    def start_if_branch(self, data: 'running.If', result: 'result.If'):
        for listener in self.listeners:
            listener.start_if_branch(data, result)

    def end_if_branch(self, data: 'running.If', result: 'result.If'):
        for listener in self.listeners:
            listener.end_if_branch(data, result)

    def start_try_branch(self, data: 'running.Try', result: 'result.TryBranch'):
        for listener in self.listeners:
            listener.start_try_branch(data, result)

    def end_try_branch(self, data: 'running.Try', result: 'result.TryBranch'):
        for listener in self.listeners:
            listener.end_try_branch(data, result)

    def start_return(self, data: 'running.Return', result: 'result.Return'):
        for listener in self.listeners:
            listener.start_return(data, result)

    def end_return(self, data: 'running.Return', result: 'result.Return'):
        for listener in self.listeners:
            listener.end_return(data, result)

    def start_continue(self, data: 'running.Continue', result: 'result.Continue'):
        for listener in self.listeners:
            listener.start_continue(data, result)

    def end_continue(self, data: 'running.Continue', result: 'result.Continue'):
        for listener in self.listeners:
            listener.end_continue(data, result)

    def start_break(self, data: 'running.Break', result: 'result.Break'):
        for listener in self.listeners:
            listener.start_break(data, result)

    def end_break(self, data: 'running.Break', result: 'result.Break'):
        for listener in self.listeners:
            listener.end_break(data, result)

    def start_error(self, data: 'running.Error', result: 'result.Error'):
        for listener in self.listeners:
            listener.start_error(data, result)

    def end_error(self, data: 'running.Error', result: 'result.Error'):
        for listener in self.listeners:
            listener.end_error(data, result)

    def start_var(self, data: 'running.Var', result: 'result.Var'):
        for listener in self.listeners:
            listener.start_var(data, result)

    def end_var(self, data: 'running.Var', result: 'result.Var'):
        for listener in self.listeners:
            listener.end_var(data, result)

    def set_log_level(self, level):
        self._is_logged.set_level(level)

    def log_message(self, message: 'model.Message'):
        if self._is_logged(message.level):
            for listener in self.listeners:
                listener.log_message(message)

    def message(self, message: 'model.Message'):
        for listener in self.listeners:
            listener.message(message)

    def imported(self, import_type, name, attrs):
        for listener in self.listeners:
            listener.imported(import_type, name, attrs)

    def output_file(self, file_type, path):
        for listener in self.listeners:
            listener.output_file(file_type, path)

    def close(self):
        for listener in self.listeners:
            listener.close()

    def __bool__(self):
        return len(self.listeners) > 0


class ListenerFacade(LoggerApi):

    def __init__(self, listener, name, version):
        self.listener = listener
        self.name = name
        self.version = version
        self._start_suite = self._get_method(listener, 'start_suite')
        self._end_suite = self._get_method(listener, 'end_suite')
        self._start_test = self._get_method(listener, 'start_test')
        self._end_test = self._get_method(listener, 'end_test')
        self._log_message = self._get_method(listener, 'log_message')
        self._message = self._get_method(listener, 'message')
        self._close = self._get_method(listener, 'close')

    def start_suite(self, data: 'running.TestSuite', result: 'result.TestSuite'):
        self._start_suite(data, result)

    def end_suite(self, data: 'running.TestSuite', result: 'result.TestSuite'):
        self._end_suite(data, result)

    def start_test(self, data: 'running.TestCase', result: 'result.TestCase'):
        self._start_test(data, result)

    def end_test(self, data: 'running.TestCase', result: 'result.TestCase'):
        self._end_test(data, result)

    def log_message(self, message: 'model.Message'):
        self._log_message(message)

    def message(self, message: 'model.Message'):
        self._message(message)

    def output_file(self, type_: str, path: str):
        method = self._get_method(self.listener, '%s_file' % type_.lower())
        method(path)

    def close(self):
        self._close()

    def _get_method(self, listener, name, prefix=''):
        for method_name in self._get_method_names(name, prefix):
            if hasattr(listener, method_name):
                return ListenerMethod(getattr(listener, method_name), self.name, self.version)
        return ListenerMethod(None, self.name, self.version)

    def _get_method_names(self, name, prefix):
        names = [name, self._toCamelCase(name)] if '_' in name else [name]
        if prefix:
            names += [prefix + name for name in names]
        return names

    def _toCamelCase(self, name):
        parts = name.split('_')
        return ''.join([parts[0]] + [part.capitalize() for part in parts[1:]])


class ListenerV2Facade(ListenerFacade):

    def __init__(self, listener, name, version):
        super().__init__(listener, name, version)
        self._start_keyword = self._get_method(listener, 'start_keyword')
        self._end_keyword = self._get_method(listener, 'end_keyword')
        self._start_for = self._start_for_iteration = self._start_while = \
            self._start_while_iteration = self._start_if_branch = \
            self._start_try_branch = self._start_return = self._start_continue = \
            self._start_break = self._start_var = self._start_error = self._start_keyword
        self._end_for = self._end_for_iteration = self._end_while = self._end_while_iteration =\
            self._end_if_branch = self._end_try_branch = self._end_return = self._end_continue =\
            self._end_break = self._end_var = self._end_error = self._end_keyword

    def imported(self, import_type: str, name: str, attrs):
        method = self._get_method(self.listener, '%s_import' % import_type.lower())
        method(name, attrs)

    def start_suite(self, data: 'running.TestSuite', result: 'result.TestSuite'):
        self._start_suite(result.name, self._suite_v2_attributes(data, result))

    def end_suite(self, data: 'running.TestSuite', result: 'result.TestSuite'):
        self._end_suite(result.name, self._suite_v2_attributes(data, result, is_end=True))

    def start_test(self, data: 'running.TestCase', result: 'result.TestCase'):
        self._start_test(result.name, self._test_v2_attributes(data, result))

    def end_test(self, data: 'running.TestCase', result: 'result.TestCase'):
        self._end_test(result.name, self._test_v2_attributes(data, result, is_end=True))

    def start_keyword(self, data: 'running.Keyword', result: 'result.Keyword'):
        attrs = self._body_item_v2_attributes(data, result, is_keyword_like=True)
        self._start_keyword(result.full_name, attrs)

    def end_keyword(self, data: 'running.Keyword', result: 'result.Keyword'):
        attrs = self._body_item_v2_attributes(data, result, is_keyword_like=True, is_end=True)
        self._end_keyword(result.full_name, attrs)

    def start_for(self, data: 'running.For', result: 'result.For'):
        self._start_for(result._log_name, self._for_v2_attributes(data, result))

    def end_for(self, data: 'running.For', result: 'result.For'):
        self._end_for(result._log_name, self._for_v2_attributes(data, result, is_end=True))

    def start_for_iteration(self, data: 'running.For', result: 'result.ForIteration'):
        attrs = self._body_item_v2_attributes(data, result)
        attrs['variables'] = dict(result.assign)
        self._start_for_iteration(result._log_name, attrs)

    def end_for_iteration(self, data: 'running.For', result: 'result.ForIteration'):
        attrs = self._body_item_v2_attributes(data, result, is_end=True)
        attrs['variables'] = dict(result.assign)
        self._end_for_iteration(result._log_name, attrs)

    def start_while(self, data: 'running.While', result: 'result.While'):
        self._start_while(result._log_name, self._while_v2_attributes(data, result))

    def end_while(self, data: 'running.While', result: 'result.While'):
        self._end_while(result._log_name, self._while_v2_attributes(data, result, is_end=True))

    def start_while_iteration(self, data: 'running.While', result: 'result.WhileIteration'):
        self._start_while_iteration(result._log_name, self._body_item_v2_attributes(data, result))

    def end_while_iteration(self, data: 'running.While', result: 'result.WhileIteration'):
        self._end_while_iteration(result._log_name, self._body_item_v2_attributes(data, result, is_end=True))

    def start_if_branch(self, data: 'running.If', result: 'result.IfBranch'):
        self._start_if_branch(result._log_name, self._if_v2_attributes(data, result))

    def end_if_branch(self, data: 'running.If', result: 'result.IfBranch'):
        self._end_if_branch(result._log_name, self._if_v2_attributes(data, result, is_end=True))

    def start_try_branch(self, data: 'running.Try', result: 'result.TryBranch'):
        self._start_try_branch(result._log_name, self._try_v2_attributes(data, result))

    def end_try_branch(self, data: 'running.Try', result: 'result.TryBranch'):
        self._end_try_branch(result._log_name, self._try_v2_attributes(data, result, is_end=True))

    def start_return(self, data: 'running.Return', result: 'result.Return'):
        attrs = self._body_item_v2_attributes(data, result)
        attrs['values'] = list(result.values)
        self._start_return(result._log_name, attrs)

    def end_return(self, data: 'running.Return', result: 'result.Return'):
        attrs = self._body_item_v2_attributes(data, result, is_end=True)
        attrs['values'] = list(result.values)
        self._end_return(result._log_name, attrs)

    def start_continue(self, data: 'running.Continue', result: 'result.Continue'):
        self._start_continue(result._log_name, self._body_item_v2_attributes(data, result))

    def end_continue(self, data: 'running.Continue', result: 'result.Continue'):
        self._end_continue(result._log_name, self._body_item_v2_attributes(data, result, is_end=True))

    def start_break(self, data: 'running.Break', result: 'result.Break'):
        self._start_break(result._log_name, self._body_item_v2_attributes(data, result))

    def end_break(self, data: 'running.Break', result: 'result.Break'):
        self._end_break(result._log_name, self._body_item_v2_attributes(data, result, is_end=True))

    def start_error(self, data: 'running.Error', result: 'result.Error'):
        self._start_error(result._log_name, self._body_item_v2_attributes(data, result))

    def end_error(self, data: 'running.Error', result: 'result.Error'):
        self._end_error(result._log_name, self._body_item_v2_attributes(data, result, is_end=True))

    def start_var(self, data: 'running.Var', result: 'result.Var'):
        self._start_var(result._log_name, self._body_item_v2_attributes(data, result))

    def end_var(self, data: 'running.Var', result: 'result.Var'):
        self._end_var(result._log_name, self._body_item_v2_attributes(data, result, is_end=True))

    def log_message(self, message: 'model.Message'):
        self._log_message(self._message_attributes(message))

    def message(self, message: 'model.Message'):
        self._message(self._message_attributes(message))

    def _suite_v2_attributes(self, data, result, is_end=False):
        attrs = {
            'id': data.id,
            'doc': result.doc,
            'metadata': dict(result.metadata),
            'starttime': result.starttime,
            'longname': result.full_name,
            'tests': [t.name for t in data.tests],
            'suites': [s.name for s in data.suites],
            'totaltests': data.test_count,
            'source': str(data.source or '')
        }
        if is_end:
            attrs.update({
                'endtime': result.endtime,
                'elapsedtime': result.elapsedtime,
                'status': result.status,
                'message': result.message,
                'statistics': result.stat_message
            })
        return attrs

    def _test_v2_attributes(self, data: 'running.TestCase', result: 'result.TestCase', is_end=False):
        attrs = {
            'id': data.id,
            'doc': result.doc,
            'tags': list(result.tags),
            'lineno': data.lineno,
            'starttime': result.starttime,
            'longname': result.full_name,
            'source': str(data.source or ''),
            'template': data.template or '',
            'originalname': data.name
        }
        if is_end:
            attrs.update({
                'endtime': result.endtime,
                'elapsedtime': result.elapsedtime,
                'status': result.status,
                'message': result.message,
            })
        return attrs

    def _for_v2_attributes(self, data: 'running.For', result: 'result.For', is_end=False):
        attrs = self._body_item_v2_attributes(data, result, is_end=is_end)
        attrs.update({
            'variables': list(result.assign),
            'flavor': result.flavor or '',
            'values': list(result.values)
        })
        if result.flavor == 'IN ENUMERATE':
            attrs['start'] = result.start
        elif result.flavor == 'IN ZIP':
            attrs['fill'] = result.fill
            attrs['mode'] = result.mode
        return attrs

    def _while_v2_attributes(self, data: 'running.While', result: 'result.While', is_end=False):
        attrs = self._body_item_v2_attributes(data, result, is_end=is_end)
        attrs.update({
            'condition': result.condition,
            'limit': result.limit,
            'on_limit_message': result.on_limit_message
            # FIXME: Add 'on_limit'
        })
        return attrs

    def _if_v2_attributes(self, data: 'running.If', result: 'result.If', is_end=False):
        attrs = self._body_item_v2_attributes(data, result, is_end=is_end)
        if result.type in (BodyItem.IF, BodyItem.ELSE_IF):
            attrs['condition'] = result.condition
        return attrs

    def _try_v2_attributes(self, data: 'running.Try', result: 'result.TryBranch', is_end=False):
        attrs = self._body_item_v2_attributes(data, result, is_end=is_end)
        if result.type == BodyItem.EXCEPT:
            attrs.update({
                'patterns': list(result.patterns),
                'pattern_type': result.pattern_type,
                'variable': result.assign
            })
        return attrs

    def _return_v2_attributes(self, data: 'running.Return', result: 'result.Return', is_end=False):
        attrs = self._body_item_v2_attributes(data, result, is_end=is_end)
        attrs['values'] = list(result.values)
        return result._log_name, attrs

    def _body_item_v2_attributes(self, data, result, is_end=False, is_keyword_like=False):
        attrs = {
            'doc': result.doc,
            'lineno': data.lineno,
            'type': result.type,
            'status': result.status,
            'starttime': result.starttime,
            'source': str(data.source or '')
        }
        if is_keyword_like:
            attrs.update({
                'kwname': result.name or '',
                'libname': result.owner or '',
                'args':  [a if is_string(a) else safe_str(a) for a in result.args],
                'assign': list(result.assign),
                'tags': list(result.tags),
            })
        else:
            attrs.update({
                'kwname': result._log_name,
                'libname': '',
                'args':  [],
                'assign': [],
                'tags': []
            })
        if is_end:
            attrs.update({
                'endtime': result.endtime,
                'elapsedtime': result.elapsedtime
            })
        return attrs

    def _message_attributes(self, msg):
        # Timestamp in our legacy format.
        timestamp = msg.timestamp.isoformat(' ', timespec='milliseconds').replace('-', '')
        attrs = {'timestamp': timestamp,
                 'message': msg.message,
                 'level': msg.level,
                 'html': 'yes' if msg.html else 'no'}
        return attrs


def import_listener(listener):
    if not is_string(listener):
        # Modules have `__name__`, with others better to use `type_name`.
        name = getattr(listener, '__name__', None) or type_name(listener)
        return listener, name
    name, args = split_args_from_name_or_path(listener)
    importer = Importer('listener', logger=LOGGER)
    listener = importer.import_class_or_module(os.path.normpath(name),
                                               instantiate_with_args=args)
    return listener, name


def get_version(listener, name):
    try:
        version = int(listener.ROBOT_LISTENER_API_VERSION)
        if version not in (2, 3):
            raise ValueError
    except AttributeError:
        raise DataError("Listener '%s' does not have mandatory "
                        "'ROBOT_LISTENER_API_VERSION' attribute."
                        % name)
    except (ValueError, TypeError):
        raise DataError("Listener '%s' uses unsupported API version '%s'."
                        % (name, listener.ROBOT_LISTENER_API_VERSION))
    return version


def import_listeners(listeners,
                     raise_on_error=False):
    all = []
    for listener in listeners:
        try:
            imported, name = import_listener(listener)
            version = get_version(imported, name)
            if version == 2:
                all.append(ListenerV2Facade(imported, name, version))
            else:
                all.append(ListenerFacade(imported, name, version))
        except DataError as err:
            name = listener if is_string(listener) else type_name(listener)
            msg = "Taking listener '%s' into use failed: %s" % (name, err)
            if raise_on_error:
                raise DataError(msg)
            LOGGER.error(msg)
    return all


class ListenerMethod:
    # Flag to avoid recursive listener calls.
    called = False

    def __init__(self, method, name, version, library=None):
        self.method = method
        self.listener_name = name
        self.version = version
        self.library = library

    def __call__(self, *args):
        if self.method is None:
            return
        if self.called:
            return
        try:
            ListenerMethod.called = True
            self.method(*args)
        except TimeoutError:
            # Propagate possible timeouts:
            # https://github.com/robotframework/robotframework/issues/2763
            raise
        except:
            message, details = get_error_details()
            LOGGER.error("Calling method '%s' of listener '%s' failed: %s"
                         % (self.method.__name__, self.listener_name, message))
            LOGGER.info("Details:\n%s" % details)
        finally:
            ListenerMethod.called = False
