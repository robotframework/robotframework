#  Copyright 2008-2009 Nokia Siemens Networks Oyj
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


import sys
from types import MethodType, FunctionType

from robot import utils
from robot.errors import FrameworkError
from robot.common import BaseHandler

from runkwregister import RUN_KW_REGISTER
from argtypes import LibraryKeywordArgTypeResolver


if utils.is_jython:
    from org.python.core import PyReflectedFunction, PyReflectedConstructor

    from javaargcoercer import ArgumentCoercer

    def _is_java_init(init):
        return isinstance(init, PyReflectedConstructor)
    def _is_java_method(method):
        return hasattr(method, 'im_func') \
               and isinstance(method.im_func, PyReflectedFunction)
else:
    _is_java_init = _is_java_method = lambda item: False


def Handler(library, name, method):
    if _is_java_method(method):
        return _JavaHandler(library, name, method)
    else:
        return _PythonHandler(library, name, method)


def InitHandler(library, method):
    if method is None:
        return _NoInitHandler(library)
    elif _is_java_init(method):
        return _JavaInitHandler(library, method)
    else:
        return _PythonInitHandler(library, method)


class _RunnableHandler(BaseHandler):
    """Base class for PythonHandler, JavaHandler and DynamicHandler"""

    type = 'library'

    def __init__(self, library, handler_name, handler_method):
        self.library = library
        self._handler_name = handler_name
        self.name = utils.printable_name(handler_name, code_style=True)
        self._method = library.scope == 'GLOBAL' and \
                self._get_global_handler(handler_method, handler_name) or None
        self.doc = ''
        self.timeout = ''  # Needed for set_attributes in runner.start_keyword

    def run(self, output, namespace, args):
        """Executes the represented handler with given 'args'.

        Note: This method MUST NOT change this object's internal state.
        """
        args = self._process_args(args, namespace.variables)
        self._tracelog_args(output, args)
        self._capture_output()
        try:
            ret = self._run_handler(self._current_handler(), args, output, 
                                    self._get_timeout(namespace))
        finally:
            self._release_and_log_output(output)
        self._tracelog_return_value(output, ret)
        return ret

    def _capture_output(self):
        utils.capture_output()

    def _current_handler(self):
        if self._method is not None:
            return self._method
        return self._get_handler(self.library.get_instance(),
                                 self._handler_name)

    def _tracelog_return_value(self, output, ret):
        output.trace('Return: %s' % utils.unic(ret))

    def _get_global_handler(self, method, name):
        return method

    def _get_handler(self, lib_instance, handler_name):
        """Overridden by DynamicHandler"""
        return getattr(lib_instance, handler_name)

    def _process_args(self, args, variables):
        index = RUN_KW_REGISTER.get_args_to_process(self.library.orig_name, self.name)
        # Negative index means that this is not Run Keyword variant and all
        # arguments are processed normally
        if index < 0:
            return self._replace_vars_from_args(args, variables)
        if index == 0:
            return self.check_arg_limits(args)
        # There might be @{list} variables and those might have more or less
        # arguments that is needed. Therefore we need to go through arguments
        # one by one.
        processed = []
        while len(processed) < index and args:
            processed += variables.replace_list([args.pop(0)])
        # In case @{list} variable is unpacked, the arguments going further
        # needs to be escaped, otherwise those are unescaped twice.
        processed[index:] = [utils.escape(arg) for arg in processed[index:]]
        return self.check_arg_limits(processed + args)

    def _replace_vars_from_args(self, args, variables):
        """Overridden by JavaHandler"""
        args = variables.replace_list(args)
        return self.check_arg_limits(args)

    def _run_handler(self, handler, args, output, timeout):
        arg_resolver = LibraryKeywordArgTypeResolver(self.args, args)
        posargs = arg_resolver.posargs
        if timeout is not None and timeout.active():
            return timeout.run(handler, args=posargs, logger=output)
        return handler(*posargs, **arg_resolver.kwargs)

    def _get_timeout(self, namespace):
        # Timeouts must not be active for run keyword variants, only for
        # keywords they execute internally
        if RUN_KW_REGISTER.is_run_keyword(self):
            return None
        timeoutable = self._get_timeoutable_items(namespace)
        if len(timeoutable) > 0 :
            return min([ item.timeout for item in timeoutable ])
        return None

    def _get_timeoutable_items(self, namespace):
        items = namespace.uk_handlers[:]
        if namespace.test is not None and namespace.test.status == 'RUNNING':
            items.append(namespace.test)
        return items

    def _release_and_log_output(self, logger):
        stdout, stderr = utils.release_output()
        logger.log_output(stdout)
        logger.log_output(stderr)
        if stderr.strip() != '':
            sys.stderr.write(stderr+'\n')


class _PythonHandler(_RunnableHandler):

    def __init__(self, library, handler_name, handler_method):
        _RunnableHandler.__init__(self, library, handler_name, handler_method)
        self.doc = utils.get_doc(handler_method)
        self.args, self.defaults, self.varargs \
                = self._get_arg_spec(handler_method)
        self.minargs = len(self.args) - len(self.defaults)
        self.maxargs = self.varargs is not None and sys.maxint or len(self.args)

    def _get_arg_spec(self, handler):
        """Returns info about args in a tuple (args, defaults, varargs)

        args     - tuple of all accepted arguments
        defaults - tuple of default values
        varargs  - name of the argument accepting varargs or None
        """
        # Code below is based on inspect module's getargs and getargspec
        # methods. See their documentation and/or source for more details.
        if type(handler) is MethodType:
            func = handler.im_func
            first_arg = 1        # this drops 'self' from methods' args
        elif type(handler) is FunctionType:
            func = handler
            first_arg = 0
        else:
            raise FrameworkError("Only MethodType and FunctionType accepted. "
                                 "Got '%s' instead." % type(handler))
        co = func.func_code
        nargs = co.co_argcount
        args = co.co_varnames[first_arg:nargs]
        defaults = func.func_defaults
        if defaults is None:
            defaults = ()
        if co.co_flags & 4:                      # 4 == CO_VARARGS
            varargs =  co.co_varnames[nargs]
        else:
            varargs = None
        return args, defaults, varargs


class _JavaHandler(_RunnableHandler):

    def __init__(self, library, handler_name, handler_method):
        _RunnableHandler.__init__(self, library, handler_name, handler_method)
        signatures = self._get_signatures(handler_method)
        self.minargs, self.maxargs = self._get_arg_limits(signatures)
        self._arg_coercer = ArgumentCoercer(signatures)

    def _get_arg_limits(self, signatures):
        if len(signatures) == 1:
            return self._get_single_sig_arg_limits(signatures[0])
        else:
            return self._get_multi_sig_arg_limits(signatures)

    def _get_code_object(self, handler):
        return handler.im_func

    def _get_signatures(self, handler):
        co = self._get_code_object(handler)
        return co.argslist[:co.nargs]

    def _get_single_sig_arg_limits(self, signature):
        args = signature.args
        if len(args) > 0 and args[-1].isArray():
            mina = len(args) - 1
            maxa = sys.maxint
        else:
            mina = maxa = len(args)
        return mina, maxa

    def _get_multi_sig_arg_limits(self, signatures):
        mina = maxa = None
        for sig in signatures:
            argc = len(sig.args)
            if mina is None or argc < mina:
                mina = argc
            if maxa is None or argc > maxa:
                maxa = argc
        return mina, maxa

    def _replace_vars_from_args(self, args, variables):
        args = _RunnableHandler._replace_vars_from_args(self, args, variables)
        if self.maxargs == sys.maxint:
            args = self._handle_varargs(args)
        return self._arg_coercer(args)

    def _handle_varargs(self, args):
        if len(args) == self.minargs:
            args.append([])
        elif len(args) == self.minargs + 1 and utils.is_list(args[-1]):
            pass
        else:
            varargs = args[self.minargs:]
            args = args[:self.minargs]
            args.append(varargs)
        return args


class DynamicHandler(_RunnableHandler):

    def __init__(self, library, handler_name, handler_method, doc='',
                 argspec=None):
        _RunnableHandler.__init__(self, library, handler_name, handler_method)
        self._run_keyword_method_name = handler_method.__name__
        self.doc = doc is not None and utils.unic(doc) or ''
        self.args, self.defaults, self.varargs = self._get_arg_spec(argspec)
        self.minargs = len(self.args) - len(self.defaults)
        self.maxargs = self.varargs is not None and sys.maxint or len(self.args)

    def _get_arg_spec(self, argspec):
        if argspec is None:
            return [], [], '<unknown>'
        try:
            if utils.is_str(argspec):
                raise TypeError
            return self._parse_arg_spec(list(argspec))
        except TypeError:
            raise TypeError('Argument specification should be list/array of Strings.')

    def _parse_arg_spec(self, argspec):
        if argspec == []:
            return [], [], None
        args = []
        defaults = []
        vararg = None
        for token in argspec:
            if vararg is not None:
                raise TypeError
            if token.startswith('*'):
                vararg = token[1:]
                continue
            if token.count('=') > 0:
                arg, default = token.split('=', 1)
                args.append(arg)
                defaults.append(default)
                continue
            if defaults:
                raise TypeError
            args.append(token)
        return args, defaults, vararg

    def _get_handler(self, lib_instance, handler_name):
        runner = getattr(lib_instance, self._run_keyword_method_name)
        return self._get_dynamic_handler(runner, handler_name)

    def _get_global_handler(self, method, name):
        return self._get_dynamic_handler(method, name)

    def _get_dynamic_handler(self, runner, name):
        def handler(*args):
            return runner(name, list(args))
        return handler


class _NoInitHandler(BaseHandler):

    def __init__(self, library):
        self.library = library
        self.minargs = 0
        self.maxargs = 0


class _PythonInitHandler(_PythonHandler):

    def __init__(self, library, handler_method):
        _PythonHandler.__init__(self, library, '__init__', handler_method)


class _JavaInitHandler(_JavaHandler):

    def __init__(self, library, handler_method):
        _JavaHandler.__init__(self, library, '__init__', handler_method)

    def _get_code_object(self, handler):
        return handler
