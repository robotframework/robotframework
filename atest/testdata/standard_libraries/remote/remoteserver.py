import sys
import inspect
from SimpleXMLRPCServer import SimpleXMLRPCServer
from xmlrpclib import Binary


class RemoteServer(SimpleXMLRPCServer):

    def __init__(self, library, port=8270):
        SimpleXMLRPCServer.__init__(self, ('127.0.0.1', int(port)))
        self.library = library
        self.register_function(self.get_keyword_names)
        self.register_function(self.get_keyword_arguments)
        self.register_function(self.run_keyword)
        self.serve_forever()

    def get_keyword_names(self):
        return [attr for attr in dir(self.library) if attr[0] != '_']

    def get_keyword_arguments(self, name):
        kw = getattr(self.library, name)
        args, varargs, kwargs, defaults = inspect.getargspec(kw)
        args = args[1:]  # drop 'self'
        if defaults:
            args, names = args[:-len(defaults)], args[-len(defaults):]
            args += ['%s=%s' % (n, d) for n, d in zip(names, defaults)]
        if varargs:
            args.append('*%s' % varargs)
        if kwargs:
            args.append('**%s' % kwargs)
        return args

    def run_keyword(self, name, args, kwargs=None):
        try:
            result = getattr(self.library, name)(*args, **(kwargs or {}))
        except AssertionError, err:
            return {'status': 'FAIL', 'error': str(err)}
        else:
            return {'status': 'PASS',
                    'return': result if result is not None else ''}


class Library(object):

    def argument_should_be(self, argument, expected, binary=False):
        if binary:
            assert isinstance(argument, Binary), 'Non-binary argument'
            argument = str(argument)
        expected = eval(expected)
        assert argument == expected, '%r != %r' % (argument, expected)

    def kwarg_should_be(self, **kwargs):
        self.argument_should_be(**kwargs)

    def return_binary(self, *ordinals):
        return Binary(''.join(chr(int(o)) for o in ordinals))

    def no_arguments(self):
        return self._format_args()

    def one_argument(self, arg):
        return self._format_args(arg)

    def two_arguments(self, arg1, arg2):
        return self._format_args(arg1, arg2)

    def five_arguments(self, arg1, arg2, arg3, arg4, arg5):
        return self._format_args(arg1, arg2, arg3, arg4, arg5)

    def arguments_with_default_values(self, arg1, arg2=2, arg3='3'):
        return self._format_args(arg1, arg2, arg3)

    def varargs(self, *args):
        return self._format_args(*args)

    def required_defaults_and_varargs(self, req, default='world', *varargs):
        return self._format_args(req, default, *varargs)

    def kwargs(self, **kwargs):
        return self._format_args(**kwargs)

    def args_and_kwargs(self, arg1='default1', arg2='default2', **kwargs):
        return self._format_args(arg1, arg2, **kwargs)

    def varargs_and_kwargs(self, *varargs, **kwargs):
        return self._format_args(*varargs, **kwargs)

    def args_varargs_and_kwargs(self, arg1='default1', arg2='default2',
                                *varargs, **kwargs):
        return self._format_args(arg1, arg2, *varargs, **kwargs)

    def _format_args(self, *args, **kwargs):
        args += tuple('%s:%s' % (k, self._type(v))
                      for k, v in sorted(kwargs.items()))
        return ', '.join(self._type(a) for a in args)

    def _type(self, arg):
        if not isinstance(arg, basestring):
            return '%s (%s)' % (arg, type(arg).__name__)
        return arg


if __name__ == '__main__':
    RemoteServer(Library(), *sys.argv[1:])
