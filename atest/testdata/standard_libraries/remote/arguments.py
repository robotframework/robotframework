import sys

from datetime import datetime    # Needed by `eval()`.
from xmlrpc.client import Binary

from remoteserver import RemoteServer, keyword


class TypedRemoteServer(RemoteServer):

    def _register_functions(self):
        RemoteServer._register_functions(self)
        self.register_function(self.get_keyword_types)

    def get_keyword_types(self, name):
        kw = getattr(self.library, name)
        return getattr(kw, 'robot_types', None)

    def get_keyword_arguments(self, name):
        if name == 'defaults_as_tuples':
            return [('first', 'eka'), ('second', 2)]
        return RemoteServer.get_keyword_arguments(self, name)


class Arguments:

    def argument_should_be(self, argument, expected, binary=False):
        if binary:
            argument = self._handle_binary(argument)
        expected = eval(expected)
        self._assert_equal(argument, expected)

    def _assert_equal(self, argument, expected, msg=None):
        assert argument == expected, msg or '%r != %r' % (argument, expected)

    def _handle_binary(self, arg, required=True):
        if isinstance(arg, list):
            return self._handle_binary_in_list(arg)
        if isinstance(arg, dict):
            return self._handle_binary_in_dict(arg)
        assert isinstance(arg, Binary) or not required, 'Non-binary argument'
        return arg.data if isinstance(arg, Binary) else arg

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

    # Handled separately by get_keyword_arguments above.
    def defaults_as_tuples(self, first='eka', second=2):
        return self._format_args(first, second)

    def kwargs(self, **kwargs):
        return self._format_args(**kwargs)

    def kw_only_arg(self, *, kwo):
        return self._format_args(kwo=kwo)

    def kw_only_arg_with_default(self, *, k1='default', k2):
        return self._format_args(k1=k1, k2=k2)

    def args_and_kwargs(self, arg1='default1', arg2='default2', **kwargs):
        return self._format_args(arg1, arg2, **kwargs)

    def varargs_and_kwargs(self, *varargs, **kwargs):
        return self._format_args(*varargs, **kwargs)

    def all_arg_types(self, arg1, arg2='default', *varargs,
                      kwo1='default', kwo2, **kwargs):
        return self._format_args(arg1, arg2, *varargs,
                                 kwo1=kwo1, kwo2=kwo2, **kwargs)

    @keyword(types=['int', '', 'dict'])
    def argument_types_as_list(self, integer, no_type_1, dictionary, no_type_2):
        self._assert_equal(integer, 42)
        self._assert_equal(no_type_1, '42')
        self._assert_equal(dictionary, {'a': 1, 'b': 'ä'})
        self._assert_equal(no_type_2, '{}')

    @keyword(types={'integer': 'Integer', 'dictionary': 'Dictionary'})
    def argument_types_as_dict(self, integer, no_type_1, dictionary, no_type_2):
        self.argument_types_as_list(integer, no_type_1, dictionary, no_type_2)

    def _format_args(self, *args, **kwargs):
        args = [self._format(a) for a in args]
        kwargs = [f'{k}:{self._format(kwargs[k])}' for k in sorted(kwargs)]
        return ', '.join(args + kwargs)

    def _format(self, arg):
        type_name = type(arg).__name__
        return arg if isinstance(arg, str) else f'{arg} ({type_name})'


if __name__ == '__main__':
    TypedRemoteServer(Arguments(), *sys.argv[1:])
