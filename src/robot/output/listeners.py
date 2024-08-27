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
from abc import ABC
from pathlib import Path

from robot.errors import DataError, TimeoutError
from robot.model import BodyItem
from robot.utils import (get_error_details, Importer, safe_str,
                         split_args_from_name_or_path, type_name)

from .loggerapi import LoggerApi
from .loggerhelper import IsLogged
from .logger import LOGGER


class Listeners:
    _listeners: 'list[ListenerFacade]'

    def __init__(self, listeners=(), log_level='INFO'):
        self._is_logged = IsLogged(log_level)
        self._listeners = self._import_listeners(listeners)

    # Must be property to allow LibraryListeners to override it.
    @property
    def listeners(self):
        return self._listeners

    def _import_listeners(self, listeners, library=None) -> 'list[ListenerFacade]':
        imported = []
        for listener_source in listeners:
            try:
                listener = self._import_listener(listener_source, library)
            except DataError as err:
                name = listener_source \
                    if isinstance(listener_source, str) else type_name(listener_source)
                msg = f"Taking listener '{name}' into use failed: {err}"
                if library:
                    raise DataError(msg)
                LOGGER.error(msg)
            else:
                imported.append(listener)
        return imported

    def _import_listener(self, listener, library=None) -> 'ListenerFacade':
        if library and isinstance(listener, str) and listener.upper() == 'SELF':
            listener = library.instance
        if isinstance(listener, str):
            name, args = split_args_from_name_or_path(listener)
            importer = Importer('listener', logger=LOGGER)
            listener = importer.import_class_or_module(os.path.normpath(name),
                                                       instantiate_with_args=args)
        else:
            # Modules have `__name__`, with others better to use `type_name`.
            name = getattr(listener, '__name__', None) or type_name(listener)
        if self._get_version(listener) == 2:
            return ListenerV2Facade(listener, name, self._is_logged, library)
        return ListenerV3Facade(listener, name, self._is_logged, library)

    def _get_version(self, listener):
        version = getattr(listener, 'ROBOT_LISTENER_API_VERSION', 3)
        try:
            version = int(version)
            if version not in (2, 3):
                raise ValueError
        except (ValueError, TypeError):
            raise DataError(f"Unsupported API version '{version}'.")
        return version

    def set_log_level(self, level):
        self._is_logged.set_level(level)

    def __iter__(self):
        return iter(self.listeners)

    def __len__(self):
        return len(self.listeners)


class LibraryListeners(Listeners):
    _listeners: 'list[list[ListenerFacade]]'

    def __init__(self, log_level='INFO'):
        super().__init__(log_level=log_level)

    @property
    def listeners(self):
        return self._listeners[-1] if self._listeners else []

    def new_suite_scope(self):
        self._listeners.append([])

    def discard_suite_scope(self):
        self._listeners.pop()

    def register(self, library):
        listeners = self._import_listeners(library.listeners, library=library)
        self._listeners[-1].extend(listeners)

    def unregister(self, library, close=False):
        remaining = []
        for listener in self._listeners[-1]:
            if listener.library is not library:
                remaining.append(listener)
            elif close:
                listener.close()
        self._listeners[-1] = remaining


class ListenerFacade(LoggerApi, ABC):

    def __init__(self, listener, name, is_logged, library=None):
        self.listener = listener
        self.name = name
        self._is_logged = is_logged
        self.library = library
        self.priority = self._get_priority(listener)

    def _get_priority(self, listener):
        priority = getattr(listener, 'ROBOT_LISTENER_PRIORITY', 0)
        try:
            return float(priority)
        except (ValueError, TypeError):
            raise DataError(f"Invalid listener priority '{priority}'.")

    def _get_method(self, name, fallback=None):
        for method_name in self._get_method_names(name):
            method = getattr(self.listener, method_name, None)
            if method:
                return ListenerMethod(method, self.name)
        return ListenerMethod(None, self.name) if fallback is None else fallback

    def _get_method_names(self, name):
        names = [name, self._to_camelCase(name)] if '_' in name else [name]
        if self.library is not None:
            names += ['_' + name for name in names]
        return names

    def _to_camelCase(self, name):
        first, *rest = name.split('_')
        return ''.join([first] + [part.capitalize() for part in rest])


class ListenerV3Facade(ListenerFacade):

    def __init__(self, listener, name, is_logged, library=None):
        super().__init__(listener, name, is_logged, library)
        get = self._get_method
        # Suite
        self.start_suite = get('start_suite')
        self.end_suite = get('end_suite')
        # Test
        self.start_test = get('start_test')
        self.end_test = get('end_test')
        # Fallbacks for body items
        start_body_item = self._get_method('start_body_item')
        end_body_item = self._get_method('end_body_item')
        # Keywords
        self.start_keyword = get('start_keyword', start_body_item)
        self.end_keyword = get('end_keyword', end_body_item)
        self._start_user_keyword = get('start_user_keyword')
        self._end_user_keyword = get('end_user_keyword')
        self._start_library_keyword = get('start_library_keyword')
        self._end_library_keyword = get('end_library_keyword')
        self._start_invalid_keyword = get('start_invalid_keyword')
        self._end_invalid_keyword = get('end_invalid_keyword')
        # IF
        self.start_if = get('start_if', start_body_item)
        self.end_if = get('end_if', end_body_item)
        self.start_if_branch = get('start_if_branch', start_body_item)
        self.end_if_branch = get('end_if_branch', end_body_item)
        # TRY
        self.start_try = get('start_try', start_body_item)
        self.end_try = get('end_try', end_body_item)
        self.start_try_branch = get('start_try_branch', start_body_item)
        self.end_try_branch = get('end_try_branch', end_body_item)
        # FOR
        self.start_for = get('start_for', start_body_item)
        self.end_for = get('end_for', end_body_item)
        self.start_for_iteration = get('start_for_iteration', start_body_item)
        self.end_for_iteration = get('end_for_iteration', end_body_item)
        # WHILE
        self.start_while = get('start_while', start_body_item)
        self.end_while = get('end_while', end_body_item)
        self.start_while_iteration = get('start_while_iteration', start_body_item)
        self.end_while_iteration = get('end_while_iteration', end_body_item)
        # VAR
        self.start_var = get('start_var', start_body_item)
        self.end_var = get('end_var', end_body_item)
        # BREAK
        self.start_break = get('start_break', start_body_item)
        self.end_break = get('end_break', end_body_item)
        # CONTINUE
        self.start_continue = get('start_continue', start_body_item)
        self.end_continue = get('end_continue', end_body_item)
        # RETURN
        self.start_return = get('start_return', start_body_item)
        self.end_return = get('end_return', end_body_item)
        # ERROR
        self.start_error = get('start_error', start_body_item)
        self.end_error = get('end_error', end_body_item)
        # Messages
        self._log_message = get('log_message')
        self.message = get('message')
        # Imports
        self.library_import = get('library_import')
        self.resource_import = get('resource_import')
        self.variables_import = get('variables_import')
        # Result files
        self.output_file = get('output_file')
        self.report_file = get('report_file')
        self.log_file = get('log_file')
        self.xunit_file = get('xunit_file')
        self.debug_file = get('debug_file')
        # Close
        self.close = get('close')

    def start_user_keyword(self, data, implementation, result):
        if self._start_user_keyword:
            self._start_user_keyword(data, implementation, result)
        else:
            self.start_keyword(data, result)

    def end_user_keyword(self, data, implementation, result):
        if self._end_user_keyword:
            self._end_user_keyword(data, implementation, result)
        else:
            self.end_keyword(data, result)

    def start_library_keyword(self, data, implementation, result):
        if self._start_library_keyword:
            self._start_library_keyword(data, implementation, result)
        else:
            self.start_keyword(data, result)

    def end_library_keyword(self, data, implementation, result):
        if self._end_library_keyword:
            self._end_library_keyword(data, implementation, result)
        else:
            self.end_keyword(data, result)

    def start_invalid_keyword(self, data, implementation, result):
        if self._start_invalid_keyword:
            self._start_invalid_keyword(data, implementation, result)
        else:
            self.start_keyword(data, result)

    def end_invalid_keyword(self, data, implementation, result):
        if self._end_invalid_keyword:
            self._end_invalid_keyword(data, implementation, result)
        else:
            self.end_keyword(data, result)

    def log_message(self, message):
        if self._is_logged(message.level):
            self._log_message(message)


class ListenerV2Facade(ListenerFacade):

    def __init__(self, listener, name, is_logged, library=None):
        super().__init__(listener, name, is_logged, library)
        # Suite
        self._start_suite = self._get_method('start_suite')
        self._end_suite = self._get_method('end_suite')
        # Test
        self._start_test = self._get_method('start_test')
        self._end_test = self._get_method('end_test')
        # Keyword and control structures
        self._start_kw = self._get_method('start_keyword')
        self._end_kw = self._get_method('end_keyword')
        # Messages
        self._log_message = self._get_method('log_message')
        self._message = self._get_method('message')
        # Imports
        self._library_import = self._get_method('library_import')
        self._resource_import = self._get_method('resource_import')
        self._variables_import = self._get_method('variables_import')
        # Result files
        self._output_file = self._get_method('output_file')
        self._report_file = self._get_method('report_file')
        self._log_file = self._get_method('log_file')
        self._xunit_file = self._get_method('xunit_file')
        self._debug_file = self._get_method('debug_file')
        # Close
        self._close = self._get_method('close')

    def start_suite(self, data, result):
        self._start_suite(result.name, self._suite_attrs(data, result))

    def end_suite(self, data, result):
        self._end_suite(result.name, self._suite_attrs(data, result, end=True))

    def start_test(self, data, result):
        self._start_test(result.name, self._test_attrs(data, result))

    def end_test(self, data, result):
        self._end_test(result.name, self._test_attrs(data, result, end=True))

    def start_keyword(self, data, result):
        self._start_kw(result.full_name, self._keyword_attrs(data, result))

    def end_keyword(self, data, result):
        self._end_kw(result.full_name, self._keyword_attrs(data, result, end=True))

    def start_for(self, data, result):
        extra = self._for_extra_attrs(result)
        self._start_kw(result._log_name, self._attrs(data, result, **extra))

    def end_for(self, data, result):
        extra = self._for_extra_attrs(result)
        self._end_kw(result._log_name, self._attrs(data, result, **extra, end=True))

    def _for_extra_attrs(self, result):
        extra = {
            'variables': list(result.assign),
            'flavor': result.flavor or '',
            'values': list(result.values)
        }
        if result.flavor == 'IN ENUMERATE':
            extra['start'] = result.start
        elif result.flavor == 'IN ZIP':
            extra['fill'] = result.fill
            extra['mode'] = result.mode
        return extra

    def start_for_iteration(self, data, result):
        attrs = self._attrs(data, result, variables=dict(result.assign))
        self._start_kw(result._log_name, attrs)

    def end_for_iteration(self, data, result):
        attrs = self._attrs(data, result, variables=dict(result.assign), end=True)
        self._end_kw(result._log_name, attrs)

    def start_while(self, data, result):
        attrs = self._attrs(data, result, condition=result.condition,
                            limit=result.limit, on_limit=result.on_limit,
                            on_limit_message=result.on_limit_message)
        self._start_kw(result._log_name, attrs)

    def end_while(self, data, result):
        attrs = self._attrs(data, result, condition=result.condition,
                            limit=result.limit, on_limit=result.on_limit,
                            on_limit_message=result.on_limit_message, end=True)
        self._end_kw(result._log_name, attrs)

    def start_while_iteration(self, data, result):
        self._start_kw(result._log_name, self._attrs(data, result))

    def end_while_iteration(self, data, result):
        self._end_kw(result._log_name, self._attrs(data, result, end=True))

    def start_if_branch(self, data, result):
        extra = {'condition': result.condition} if result.type != result.ELSE else {}
        self._start_kw(result._log_name, self._attrs(data, result, **extra))

    def end_if_branch(self, data, result):
        extra = {'condition': result.condition} if result.type != result.ELSE else {}
        self._end_kw(result._log_name, self._attrs(data, result, **extra, end=True))

    def start_try_branch(self, data, result):
        extra = self._try_extra_attrs(result)
        self._start_kw(result._log_name, self._attrs(data, result, **extra))

    def end_try_branch(self, data, result):
        extra = self._try_extra_attrs(result)
        self._end_kw(result._log_name, self._attrs(data, result, **extra, end=True))

    def _try_extra_attrs(self, result):
        if result.type == BodyItem.EXCEPT:
            return {
                'patterns': list(result.patterns),
                'pattern_type': result.pattern_type,
                'variable': result.assign
            }
        return {}

    def start_return(self, data, result):
        attrs = self._attrs(data, result, values=list(result.values))
        self._start_kw(result._log_name, attrs)

    def end_return(self, data, result):
        attrs = self._attrs(data, result, values=list(result.values), end=True)
        self._end_kw(result._log_name, attrs)

    def start_continue(self, data, result):
        self._start_kw(result._log_name, self._attrs(data, result))

    def end_continue(self, data, result):
        self._end_kw(result._log_name, self._attrs(data, result, end=True))

    def start_break(self, data, result):
        self._start_kw(result._log_name, self._attrs(data, result))

    def end_break(self, data, result):
        self._end_kw(result._log_name, self._attrs(data, result, end=True))

    def start_error(self, data, result):
        self._start_kw(result._log_name, self._attrs(data, result))

    def end_error(self, data, result):
        self._end_kw(result._log_name, self._attrs(data, result, end=True))

    def start_var(self, data, result):
        extra = self._var_extra_attrs(result)
        self._start_kw(result._log_name, self._attrs(data, result, **extra))

    def end_var(self, data, result):
        extra = self._var_extra_attrs(result)
        self._end_kw(result._log_name, self._attrs(data, result, **extra, end=True))

    def _var_extra_attrs(self, result):
        if result.name.startswith('$'):
            value = (result.separator or ' ').join(result.value)
        else:
            value = list(result.value)
        return {'name': result.name, 'value': value, 'scope': result.scope or 'LOCAL'}

    def log_message(self, message):
        if self._is_logged(message.level):
            self._log_message(self._message_attributes(message))

    def message(self, message):
        self._message(self._message_attributes(message))

    def library_import(self, library, importer):
        self._library_import(library.name, {'args': list(importer.args),
                                            'originalname': library.real_name,
                                            'source': str(library.source or ''),
                                            'importer': str(importer.source)})

    def resource_import(self, resource, importer):
        self._resource_import(resource.name, {'source': str(resource.source),
                                              'importer': str(importer.source)})

    def variables_import(self, attrs: dict, importer):
        self._variables_import(attrs['name'], {'args': list(attrs['args']),
                                               'source': str(attrs['source']),
                                               'importer': str(importer.source)})

    def output_file(self, path: Path):
        self._output_file(str(path))

    def report_file(self, path: Path):
        self._report_file(str(path))

    def log_file(self, path: Path):
        self._log_file(str(path))

    def xunit_file(self, path: Path):
        self._xunit_file(str(path))

    def debug_file(self, path: Path):
        self._debug_file(str(path))

    def _suite_attrs(self, data, result, end=False):
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
        if end:
            attrs.update({
                'endtime': result.endtime,
                'elapsedtime': result.elapsedtime,
                'status': result.status,
                'message': result.message,
                'statistics': result.stat_message
            })
        return attrs

    def _test_attrs(self, data, result, end=False):
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
        if end:
            attrs.update({
                'endtime': result.endtime,
                'elapsedtime': result.elapsedtime,
                'status': result.status,
                'message': result.message,
            })
        return attrs

    def _keyword_attrs(self, data, result, end=False):
        attrs = {
            'doc': result.doc,
            'lineno': data.lineno,
            'type': result.type,
            'status': result.status,
            'starttime': result.starttime,
            'source': str(data.source or ''),
            'kwname': result.name or '',
            'libname': result.owner or '',
            'args':  [a if isinstance(a, str) else safe_str(a) for a in result.args],
            'assign': list(result.assign),
            'tags': list(result.tags)
        }
        if end:
            attrs.update({
                'endtime': result.endtime,
                'elapsedtime': result.elapsedtime
            })
        return attrs

    def _attrs(self, data, result, end=False, **extra):
        attrs = {
            'doc': '',
            'lineno': data.lineno,
            'type': result.type,
            'status': result.status,
            'starttime': result.starttime,
            'source': str(data.source or ''),
            'kwname': result._log_name,
            'libname': '',
            'args':  [],
            'assign': [],
            'tags': []
        }
        attrs.update(**extra)
        if end:
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

    def close(self):
        self._close()


class ListenerMethod:
    # Flag to avoid recursive listener calls.
    called = False

    def __init__(self, method, name):
        self.method = method
        self.listener_name = name

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
        except Exception:
            message, details = get_error_details()
            LOGGER.error(f"Calling method '{self.method.__name__}' of listener "
                         f"'{self.listener_name}' failed: {message}")
            LOGGER.info(f"Details:\n{details}")
        finally:
            ListenerMethod.called = False

    def __bool__(self):
        return self.method is not None
