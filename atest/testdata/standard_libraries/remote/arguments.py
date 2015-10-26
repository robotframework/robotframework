import sys
from xmlrpclib import Binary

from remoteserver import RemoteServer


class Arguments(object):

    def argument_should_be(self, argument, expected, binary=False):
        if binary:
            argument = self._handle_binary(argument)
        expected = eval(expected)
        assert argument == expected, '%r != %r' % (argument, expected)

    def _handle_binary(self, arg, required=True):
        if isinstance(arg, list):
            return self._handle_binary_in_list(arg)
        if isinstance(arg, dict):
            return self._handle_binary_in_dict(arg)
        assert isinstance(arg, Binary) or not required, 'Non-binary argument'
        return str(arg) if isinstance(arg, Binary) else arg

    def _handle_binary_in_list(self, arg):
        assert any(isinstance(a, Binary) for a in arg), 'No binary in list'
        return [self._handle_binary(a, required=False) for a in arg]

    def _handle_binary_in_dict(self, arg):
        assert any(isinstance(key, Binary) or isinstance(value, Binary)
                   for key, value in arg.items()), 'No binary in dict'
        return dict((self._handle_binary(key, required=False),
                     self._handle_binary(value, required=False))
                    for key, value in arg.items())

    def kwarg_should_be(self, **kwargs):
        self.argument_should_be(**kwargs)

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
    RemoteServer(Arguments(), *sys.argv[1:])
