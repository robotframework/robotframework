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

from contextlib import contextmanager

import http.client
import re
import socket
import sys
import xmlrpc.client
from datetime import date, datetime, timedelta
from xml.parsers.expat import ExpatError

from robot.errors import RemoteError
from robot.utils import (DotDict, is_bytes, is_dict_like, is_list_like, is_number,
                         is_string, safe_str, timestr_to_secs)


class Remote:
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, uri='http://127.0.0.1:8270', timeout=None):
        """Connects to a remote server at ``uri``.

        Optional ``timeout`` can be used to specify a timeout to wait when
        initially connecting to the server and if a connection accidentally
        closes. Timeout can be given as seconds (e.g. ``60``) or using
        Robot Framework time format (e.g. ``60s``, ``2 minutes 10 seconds``).

        The default timeout is typically several minutes, but it depends on
        the operating system and its configuration. Notice that setting
        a timeout that is shorter than keyword execution time will interrupt
        the keyword.
        """
        if '://' not in uri:
            uri = 'http://' + uri
        if timeout:
            timeout = timestr_to_secs(timeout)
        self._uri = uri
        self._client = XmlRpcRemoteClient(uri, timeout)
        self._lib_info = None
        self._lib_info_initialized = False

    def get_keyword_names(self):
        if self._is_lib_info_available():
            return [name for name in self._lib_info
                    if not (name[:2] == '__' and name[-2:] == '__')]
        try:
            return self._client.get_keyword_names()
        except TypeError as error:
            raise RuntimeError(f'Connecting remote server at {self._uri} '
                               f'failed: {error}')

    def _is_lib_info_available(self):
        if not self._lib_info_initialized:
            try:
                self._lib_info = self._client.get_library_information()
            except TypeError:
                pass
            self._lib_info_initialized = True
        return self._lib_info is not None

    def get_keyword_arguments(self, name):
        return self._get_kw_info(name, 'args', self._client.get_keyword_arguments,
                                 default=['*args'])

    def _get_kw_info(self, kw, info, getter, default=None):
        if self._is_lib_info_available():
            return self._lib_info[kw].get(info, default)
        try:
            return getter(kw)
        except TypeError:
            return default

    def get_keyword_types(self, name):
        return self._get_kw_info(name, 'types', self._client.get_keyword_types,
                                 default=())

    def get_keyword_tags(self, name):
        return self._get_kw_info(name, 'tags', self._client.get_keyword_tags)

    def get_keyword_documentation(self, name):
        return self._get_kw_info(name, 'doc', self._client.get_keyword_documentation)

    def run_keyword(self, name, args, kwargs):
        coercer = ArgumentCoercer()
        args = coercer.coerce(args)
        kwargs = coercer.coerce(kwargs)
        result = RemoteResult(self._client.run_keyword(name, args, kwargs))
        sys.stdout.write(result.output)
        if result.status != 'PASS':
            raise RemoteError(result.error, result.traceback, result.fatal,
                              result.continuable)
        return result.return_


class ArgumentCoercer:
    binary = re.compile('[\x00-\x08\x0B\x0C\x0E-\x1F]')

    def coerce(self, argument):
        for handles, handler in [(is_string, self._handle_string),
                                 (self._no_conversion_needed, self._pass_through),
                                 (self._is_date, self._handle_date),
                                 (self._is_timedelta, self._handle_timedelta),
                                 (is_dict_like, self._coerce_dict),
                                 (is_list_like, self._coerce_list)]:
            if handles(argument):
                return handler(argument)
        return self._to_string(argument)

    def _no_conversion_needed(self, arg):
        return is_number(arg) or is_bytes(arg) or isinstance(arg, datetime)

    def _handle_string(self, arg):
        if self.binary.search(arg):
            return self._handle_binary_in_string(arg)
        return arg

    def _handle_binary_in_string(self, arg):
        try:
            # Map Unicode code points to bytes directly
            return arg.encode('latin-1')
        except UnicodeError:
            raise ValueError(f'Cannot represent {arg!r} as binary.')

    def _pass_through(self, arg):
        return arg

    def _is_date(self, arg):
        return isinstance(arg, date)

    def _handle_date(self, arg):
        return datetime(arg.year, arg.month, arg.day)

    def _is_timedelta(self, arg):
        return isinstance(arg, timedelta)

    def _handle_timedelta(self, arg):
        return arg.total_seconds()

    def _coerce_list(self, arg):
        return [self.coerce(item) for item in arg]

    def _coerce_dict(self, arg):
        return {self._to_key(key): self.coerce(arg[key]) for key in arg}

    def _to_key(self, item):
        item = self._to_string(item)
        self._validate_key(item)
        return item

    def _to_string(self, item):
        item = safe_str(item) if item is not None else ''
        return self._handle_string(item)

    def _validate_key(self, key):
        if isinstance(key, bytes):
            raise ValueError(f'Dictionary keys cannot be binary. Got {key!r}.')


class RemoteResult:

    def __init__(self, result):
        if not (is_dict_like(result) and 'status' in result):
            raise RuntimeError(f'Invalid remote result dictionary: {result!r}')
        self.status = result['status']
        self.output = safe_str(self._get(result, 'output'))
        self.return_ = self._get(result, 'return')
        self.error = safe_str(self._get(result, 'error'))
        self.traceback = safe_str(self._get(result, 'traceback'))
        self.fatal = bool(self._get(result, 'fatal', False))
        self.continuable = bool(self._get(result, 'continuable', False))

    def _get(self, result, key, default=''):
        value = result.get(key, default)
        return self._convert(value)

    def _convert(self, value):
        if is_dict_like(value):
            return DotDict((k, self._convert(v)) for k, v in value.items())
        if is_list_like(value):
            return [self._convert(v) for v in value]
        return value


class XmlRpcRemoteClient:

    def __init__(self, uri, timeout=None):
        self.uri = uri
        self.timeout = timeout

    @property
    @contextmanager
    def _server(self):
        if self.uri.startswith('https://'):
            transport = TimeoutHTTPSTransport(timeout=self.timeout)
        else:
            transport = TimeoutHTTPTransport(timeout=self.timeout)
        server = xmlrpc.client.ServerProxy(self.uri, encoding='UTF-8',
                                           use_builtin_types=True,
                                           transport=transport)
        try:
            yield server
        except (socket.error, xmlrpc.client.Error) as err:
            raise TypeError(err)
        finally:
            server('close')()

    def get_library_information(self):
        with self._server as server:
            return server.get_library_information()

    def get_keyword_names(self):
        with self._server as server:
            return server.get_keyword_names()

    def get_keyword_arguments(self, name):
        with self._server as server:
            return server.get_keyword_arguments(name)

    def get_keyword_types(self, name):
        with self._server as server:
            return server.get_keyword_types(name)

    def get_keyword_tags(self, name):
        with self._server as server:
            return server.get_keyword_tags(name)

    def get_keyword_documentation(self, name):
        with self._server as server:
            return server.get_keyword_documentation(name)

    def run_keyword(self, name, args, kwargs):
        with self._server as server:
            run_keyword_args = [name, args, kwargs] if kwargs else [name, args]
            try:
                return server.run_keyword(*run_keyword_args)
            except xmlrpc.client.Fault as err:
                message = err.faultString
            except socket.error as err:
                message = f'Connection to remote server broken: {err}'
            except ExpatError as err:
                message = (f'Processing XML-RPC return value failed. '
                           f'Most often this happens when the return value '
                           f'contains characters that are not valid in XML. '
                           f'Original error was: ExpatError: {err}')
            raise RuntimeError(message)


# Custom XML-RPC timeouts based on
# http://stackoverflow.com/questions/2425799/timeout-for-xmlrpclib-client-requests

class TimeoutHTTPTransport(xmlrpc.client.Transport):
    _connection_class = http.client.HTTPConnection

    def __init__(self, timeout=None):
        super().__init__(use_builtin_types=True)
        self.timeout = timeout or socket._GLOBAL_DEFAULT_TIMEOUT

    def make_connection(self, host):
        if self._connection and host == self._connection[0]:
            return self._connection[1]
        chost, self._extra_headers, x509 = self.get_host_info(host)
        self._connection = host, self._connection_class(chost, timeout=self.timeout)
        return self._connection[1]


class TimeoutHTTPSTransport(TimeoutHTTPTransport):
    _connection_class = http.client.HTTPSConnection
