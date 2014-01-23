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

import re
import socket
import sys
import time
import xmlrpclib
try:
    from xml.parsers.expat import ExpatError
except ImportError:   # No expat in IronPython 2.7
    class ExpatError(Exception):
        pass

from robot.errors import RemoteError
from robot.utils import is_list_like, is_dict_like, unic


IRONPYTHON = sys.platform == 'cli'


class Remote(object):
    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    def __init__(self, uri='http://127.0.0.1:8270'):
        if '://' not in uri:
            uri = 'http://' + uri
        self._uri = uri
        self._client = XmlRpcRemoteClient(uri)

    def get_keyword_names(self, attempts=5):
        for i in range(attempts):
            try:
                return self._client.get_keyword_names()
            except TypeError, err:
                time.sleep(1)
        raise RuntimeError('Connecting remote server at %s failed: %s'
                           % (self._uri, err))

    def get_keyword_arguments(self, name):
        try:
            return self._client.get_keyword_arguments(name)
        except TypeError:
            return ['*args']

    def get_keyword_documentation(self, name):
        try:
            return self._client.get_keyword_documentation(name)
        except TypeError:
            return None

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


class ArgumentCoercer(object):
    binary = re.compile('[\x00-\x08\x0B\x0C\x0E-\x1F]')
    non_ascii = re.compile('[\x80-\xff]')

    def coerce(self, argument):
        for handles, handle in [(self._is_string, self._handle_string),
                                (self._is_number, self._pass_through),
                                (is_list_like, self._coerce_list),
                                (is_dict_like, self._coerce_dict),
                                (lambda arg: True, self._to_string)]:
            if handles(argument):
                return handle(argument)

    def _is_string(self, arg):
        return isinstance(arg, basestring)

    def _is_number(self, arg):
        return isinstance(arg, (int, long, float))

    def _handle_string(self, arg):
        if self._contains_binary(arg):
            return self._handle_binary(arg)
        return arg

    def _contains_binary(self, arg):
        return (self.binary.search(arg) or
                isinstance(arg, str) and not IRONPYTHON and
                self.non_ascii.search(arg))

    def _handle_binary(self, arg):
        try:
            arg = str(arg)
        except UnicodeError:
            raise ValueError('Cannot represent %r as binary.' % arg)
        return xmlrpclib.Binary(arg)

    def _pass_through(self, arg):
        return arg

    def _coerce_list(self, arg):
        return [self.coerce(item) for item in arg]

    def _coerce_dict(self, arg):
        return dict((self._to_key(key), self.coerce(arg[key])) for key in arg)

    def _to_key(self, item):
        item = self._to_string(item)
        if IRONPYTHON:
            self._validate_key_on_ironpython(item)
        return item

    def _to_string(self, item):
        item = unic(item) if item is not None else ''
        return self._handle_string(item)

    def _validate_key_on_ironpython(self, item):
        try:
            return str(item)
        except UnicodeError:
            raise ValueError('Dictionary keys cannot contain non-ASCII '
                             'characters on IronPython. Got %r.' % item)


class RemoteResult(object):

    def __init__(self, result):
        if not (is_dict_like(result) and 'status' in result):
            raise RuntimeError('Invalid remote result dictionary: %s' % result)
        self.status = result['status']
        self.output = self._get(result, 'output')
        self.return_ = self._get(result, 'return')
        self.error = self._get(result, 'error')
        self.traceback = self._get(result, 'traceback')
        self.fatal = bool(self._get(result, 'fatal', False))
        self.continuable = bool(self._get(result, 'continuable', False))

    def _get(self, result, key, default=''):
        value = result.get(key, default)
        return self._handle_binary(value)

    def _handle_binary(self, value):
        if isinstance(value, xmlrpclib.Binary):
            return str(value)
        if is_list_like(value):
            return [self._handle_binary(v) for v in value]
        if is_dict_like(value):
            return dict((k, self._handle_binary(v)) for k, v in value.items())
        return value


class XmlRpcRemoteClient(object):

    def __init__(self, uri):
        self._server = xmlrpclib.ServerProxy(uri, encoding='UTF-8')

    def get_keyword_names(self):
        try:
            return self._server.get_keyword_names()
        except socket.error, (errno, err):
            raise TypeError(err)
        except xmlrpclib.Error, err:
            raise TypeError(err)

    def get_keyword_arguments(self, name):
        try:
            return self._server.get_keyword_arguments(name)
        except xmlrpclib.Error:
            raise TypeError

    def get_keyword_documentation(self, name):
        try:
            return self._server.get_keyword_documentation(name)
        except xmlrpclib.Error:
            raise TypeError

    def run_keyword(self, name, args, kwargs):
        run_keyword_args = [name, args, kwargs] if kwargs else [name, args]
        try:
            return self._server.run_keyword(*run_keyword_args)
        except xmlrpclib.Fault, err:
            message = err.faultString
        except socket.error, err:
            message = 'Connection to remote server broken: %s' % err
        except ExpatError, err:
            message = ('Processing XML-RPC return value failed. '
                       'Most often this happens when the return value '
                       'contains characters that are not valid in XML. '
                       'Original error was: ExpatError: %s' % err)
        raise RuntimeError(message)
