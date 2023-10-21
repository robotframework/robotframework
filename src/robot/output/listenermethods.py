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

from robot.errors import TimeoutError
from robot.model import BodyItem
from robot.utils import get_error_details, is_string, safe_str

from .listenerarguments import ListenerArguments
from .logger import LOGGER


class ListenerMethods:

    def __init__(self, method_name, listeners):
        self._methods = []
        self._method_name = method_name
        if listeners:
            self._register_methods(method_name, listeners)

    def _register_methods(self, method_name, listeners):
        for listener in listeners:
            method = getattr(listener, method_name)
            if method:
                self._methods.append(ListenerMethod(method, listener))

    def start_suite(self, data: 'running.TestSuite', result: 'result.TestSuite'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._suite_v2_attributes(data, result))

    def end_suite(self, data: 'running.TestSuite', result: 'result.TestSuite'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._suite_v2_attributes(data, result, is_end=True))

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
        return result.name, attrs

    def start_test(self, data: 'running.TestCase', result: 'result.TestCase'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._test_v2_attributes(data, result))

    def end_test(self, data: 'running.TestCase', result: 'result.TestCase'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._test_v2_attributes(data, result, is_end=True))

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
        return result.name, attrs

    def start_keyword(self, data, result):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._kw_v2_attributes(data, result, is_end=False))

    def end_keyword(self, data, result):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._kw_v2_attributes(data, result, is_end=True))

    def start_for(self, data: 'running.For', result: 'result.For'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._for_v2_attributes(data, result, is_end=False))

    def end_for(self, data: 'running.For', result: 'result.For'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._for_v2_attributes(data, result, is_end=True))

    def start_for_iteration(self, data: 'running.For', result: 'result.ForIteration'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=False)
                attrs['variables'] = dict(result.assign)
                method((result._log_name, attrs))

    def end_for_iteration(self, data: 'running.For', result: 'result.ForIteration'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=True)
                attrs['variables'] = dict(result.assign)
                method((result._log_name, attrs))

    def start_while_iteration(self, data: 'running.While', result: 'result.WhileIteration'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=False)
                method((result._log_name, attrs))

    def end_while_iteration(self, data: 'running.While', result: 'result.WhileIteration'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=True)
                method((result._log_name, attrs))

    def start_while(self, data: 'running.While', result: 'result.While'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._while_v2_attributes(data, result, is_end=False))

    def end_while(self, data: 'running.While', result: 'result.While'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._while_v2_attributes(data, result, is_end=True))

    def start_if_branch(self, data: 'running.If', result: 'result.If'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._if_v2_attributes(data, result, is_end=False))

    def end_if_branch(self, data: 'running.If', result: 'result.If'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._if_v2_attributes(data, result, is_end=True))

    def start_try_branch(self, data: 'running.Try', result: 'result.TryBranch'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._try_v2_attributes(data, result, is_end=False))

    def end_try_branch(self, data: 'running.Try', result: 'result.TryBranch'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._try_v2_attributes(data, result, is_end=True))

    def start_return(self, data: 'running.Return', result: 'result.Return'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._return_v2_attributes(data, result, is_end=False))

    def end_return(self, data: 'running.Return', result: 'result.Return'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                method(self._return_v2_attributes(data, result, is_end=True))

    def start_continue(self, data: 'running.Continue', result: 'result.Continue'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=False)
                method((result._log_name, attrs))

    def end_continue(self, data: 'running.Continue', result: 'result.Continue'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=True)
                method((result._log_name, attrs))

    def start_break(self, data: 'running.Break', result: 'result.Break'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=False)
                method((result._log_name, attrs))

    def end_break(self, data: 'running.Break', result: 'result.Break'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=True)
                method((result._log_name, attrs))

    def start_error(self, data: 'running.Error', result: 'result.Error'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=False)
                method((result._log_name, attrs))

    def end_error(self, data: 'running.Error', result: 'result.Error'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=True)
                method((result._log_name, attrs))

    def start_var(self, data: 'running.Var', result: 'result.Var'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=False)
                method((result._log_name, attrs))

    def end_var(self, data: 'running.Var', result: 'result.Var'):
        for method in self._methods:
            if method.version == 3:
                method((data, result))
            else:
                attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=True)
                method((result._log_name, attrs))

    def _common_v2_attributes(self, data, result, is_keyword_like, is_end):
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

    def _kw_v2_attributes(self, data, result, is_end):
        attrs = self._common_v2_attributes(data, result, is_keyword_like=True, is_end=is_end)
        return result.full_name, attrs

    def _for_v2_attributes(self, data: 'running.For', result: 'result.For', is_end):
        attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=is_end)
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
        return result._log_name, attrs

    def _while_v2_attributes(self, data: 'running.While', result: 'result.While', is_end=False):
        attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=is_end)
        attrs.update({
            'condition': result.condition,
            'limit': result.limit,
            'on_limit_message': result.on_limit_message
            # FIXME: Add 'on_limit'
        })
        return result._log_name, attrs

    def _if_v2_attributes(self, data: 'running.If', result: 'result.If', is_end=False):
        attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=is_end)
        if result.type in (BodyItem.IF, BodyItem.ELSE_IF):
            attrs['condition'] = result.condition
        return result._log_name, attrs

    def _try_v2_attributes(self, data: 'running.Try', result: 'result.TryBranch', is_end=False):
        attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=is_end)
        if result.type == BodyItem.EXCEPT:
            attrs.update({
                'patterns': list(result.patterns),
                'pattern_type': result.pattern_type,
                'variable': result.assign
            })
        return result._log_name, attrs

    def _return_v2_attributes(self, data: 'running.Return', result: 'result.Return', is_end=False):
        attrs = self._common_v2_attributes(data, result, is_keyword_like=False, is_end=is_end)
        attrs['values'] = list(result.values)
        return result._log_name, attrs

    def __call__(self, *args):
        if self._methods:
            args = ListenerArguments.by_method_name(self._method_name, args)
            for method in self._methods:
                method(args.get_arguments(method.version))

    def __bool__(self):
        return bool(self._methods)


class LibraryListenerMethods:

    def __init__(self, method_name):
        self._method_stack = []
        self._method_name = method_name

    def new_suite_scope(self):
        self._method_stack.append([])

    def discard_suite_scope(self):
        self._method_stack.pop()

    def register(self, listeners, library):
        methods = self._method_stack[-1]
        for listener in listeners:
            method = getattr(listener, self._method_name)
            if method:
                info = ListenerMethod(method, listener, library)
                methods.append(info)

    def unregister(self, library):
        methods = [m for m in self._method_stack[-1] if m.library is not library]
        self._method_stack[-1] = methods

    def __call__(self, *args, **conf):
        methods = self._get_methods(**conf)
        if methods:
            args = ListenerArguments.by_method_name(self._method_name, args)
            for method in methods:
                method(args.get_arguments(method.version))

    def _get_methods(self, library=None):
        if not (self._method_stack and self._method_stack[-1]):
            return []
        methods = self._method_stack[-1]
        if library:
            return [m for m in methods if m.library is library]
        return methods


class ListenerMethod:
    # Flag to avoid recursive listener calls.
    called = False

    def __init__(self, method, listener, library=None):
        self.method = method
        self.listener_name = listener.name
        self.version = listener.version
        self.library = library

    def __call__(self, args):
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
