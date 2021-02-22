import sys
import unittest

from robot.errors import DataError
from robot.model import Body
from robot.running.userkeyword import EmbeddedArgumentsHandler
from robot.running.arguments import EmbeddedArguments, UserKeywordArgumentParser
from robot.utils.asserts import (assert_equal, assert_true, assert_raises,
                                 assert_raises_with_msg)


class Fake(object):
    value = ''
    message = ''

    def __iter__(self):
        return iter([])


class FakeArgs(object):

    def __init__(self, args):
        self.value = args

    def __nonzero__(self):
        return bool(self.value)

    def __iter__(self):
        return iter(self.value)


class HandlerDataMock:

    def __init__(self, name, args=[]):
        self.name = name
        self.args = FakeArgs(args)
        self.body = Body()
        self.source = None
        self.lineno = -1
        self.return_value = None
        self.doc = Fake()
        self.timeout = Fake()
        self.return_ = Fake()
        self.tags = ()
        self.teardown = None


def EAT(name, args=[]):
    handler = HandlerDataMock(name, args)
    embedded = EmbeddedArguments(name)
    return EmbeddedArgumentsHandler(handler, 'resource', embedded)


class TestEmbeddedArgs(unittest.TestCase):

    def setUp(self):
        self.tmp1 = EAT('User selects ${item} from list')
        self.tmp2 = EAT('${x} * ${y} from "${z}"')

    def test_no_embedded_args(self):
        assert_true(not EmbeddedArguments('No embedded args here'))
        assert_true(EmbeddedArguments('${Yes} embedded args here'))

    def test_get_embedded_arg_and_regexp(self):
        assert_equal(self.tmp1.embedded_args, ['item'])
        assert_equal(self.tmp1.embedded_name.pattern,
                     '^User\\ selects\\ (.*?)\\ from\\ list$')
        assert_equal(self.tmp1.name, 'User selects ${item} from list')

    def test_get_multiple_embedded_args_and_regexp(self):
        assert_equal(self.tmp2.embedded_args, ['x', 'y', 'z'])
        quote = '"' if sys.version_info[:2] >= (3, 7) else '\\"'
        assert_equal(self.tmp2.embedded_name.pattern,
                     '^(.*?)\\ \\*\\ (.*?)\\ from\\ {0}(.*?){0}$'.format(quote))

    def test_create_runner_when_no_match(self):
        assert_raises(ValueError, self.tmp1.create_runner, 'Not matching')

    def test_create_runner_with_one_embedded_arg(self):
        runner = self.tmp1.create_runner('User selects book from list')
        assert_equal(runner.embedded_args, [('item', 'book')])
        assert_equal(runner.name, 'User selects book from list')
        assert_equal(runner.longname, 'resource.User selects book from list')
        runner = self.tmp1.create_runner('User selects radio from list')
        assert_equal(runner.embedded_args, [('item', 'radio')])
        assert_equal(runner.name, 'User selects radio from list')
        assert_equal(runner.longname, 'resource.User selects radio from list')

    def test_create_runner_with_many_embedded_args(self):
        runner = self.tmp2.create_runner('User * book from "list"')
        assert_equal(runner.embedded_args,
                     [('x', 'User'), ('y', 'book'), ('z', 'list')])

    def test_create_runner_with_empty_embedded_arg(self):
        runner = self.tmp1.create_runner('User selects  from list')
        assert_equal(runner.embedded_args, [('item', '')])

    def test_create_runner_with_special_characters_in_embedded_args(self):
        runner = self.tmp2.create_runner('Janne & Heikki * "enjoy" from """')
        assert_equal(runner.embedded_args,
                     [('x', 'Janne & Heikki'), ('y', '"enjoy"'), ('z', '"')])

    def test_embedded_args_without_separators(self):
        template = EAT('This ${does}${not} work so well')
        runner = template.create_runner('This doesnot work so well')
        assert_equal(runner.embedded_args, [('does', ''), ('not', 'doesnot')])

    def test_embedded_args_with_separators_in_values(self):
        template = EAT('This ${could} ${work}-${OK}')
        runner = template.create_runner("This doesn't really work---")
        assert_equal(runner.embedded_args,
                     [('could', "doesn't"), ('work', 'really work'), ('OK', '--')])

    def test_creating_runners_is_case_insensitive(self):
        runner = self.tmp1.create_runner('User SELECts book frOm liST')
        assert_equal(runner.embedded_args, [('item', 'book')])
        assert_equal(runner.name, 'User SELECts book frOm liST')
        assert_equal(runner.longname, 'resource.User SELECts book frOm liST')


class TestGetArgSpec(unittest.TestCase):

    def test_no_args(self):
        self._verify('')

    def test_args(self):
        self._verify('${arg1}', ['arg1',])
        self._verify('${a1} ${a2}', ['a1', 'a2'])

    def test_defaults(self):
        self._verify('${arg1} ${arg2}=default @{varargs}',
                     args=['arg1', 'arg2'],
                     defaults={'arg2': 'default'},
                     varargs='varargs')
        self._verify('${arg1} ${arg2}= @{varargs}',
                     args=['arg1', 'arg2'],
                     defaults={'arg2': ''},
                     varargs='varargs')
        self._verify('${arg1}=d1 ${arg2}=d2 ${arg3}=d3',
                     args=['arg1', 'arg2', 'arg3'],
                     defaults={'arg1': 'd1', 'arg2': 'd2', 'arg3': 'd3'})

    def test_vararg(self):
        self._verify('@{varargs}', varargs='varargs')
        self._verify('${arg} @{varargs}', ['arg'], varargs='varargs')

    def test_kwonly(self):
        self._verify('@{} ${ko1} ${ko2}',
                     kwonlyargs=['ko1', 'ko2'])
        self._verify('@{vars} ${ko1} ${ko2}',
                     varargs='vars',
                     kwonlyargs=['ko1', 'ko2'])

    def test_kwonlydefaults(self):
        self._verify('@{} ${ko1} ${ko2}=xxx',
                     kwonlyargs=['ko1', 'ko2'],
                     defaults={'ko2': 'xxx'})
        self._verify('@{} ${ko1}=xxx ${ko2}',
                     kwonlyargs=['ko1', 'ko2'],
                     defaults={'ko1': 'xxx'})
        self._verify('@{v} ${ko1}=foo ${ko2} ${ko3}=',
                     varargs='v',
                     kwonlyargs=['ko1', 'ko2', 'ko3'],
                     defaults={'ko1': 'foo', 'ko3': ''})

    def test_kwargs(self):
        self._verify('&{kwargs}', kwargs='kwargs')
        self._verify('${arg} &{kwargs}',
                     args=['arg'],
                     kwargs='kwargs')
        self._verify('@{} ${arg} &{kwargs}',
                     kwonlyargs=['arg'],
                     kwargs='kwargs')
        self._verify('${a1} ${a2}=ad @{vars} ${k1} ${k2}=kd &{kws}',
                     args=['a1', 'a2'],
                     varargs='vars',
                     kwonlyargs=['k1', 'k2'],
                     defaults={'a2': 'ad', 'k2': 'kd'},
                     kwargs='kws')

    def _verify(self, in_args, args=[], defaults={}, varargs=None,
                kwonlyargs=[], kwargs=None):
        argspec = self._parse(in_args)
        assert_equal(argspec.positional, args)
        assert_equal(argspec.defaults, defaults)
        assert_equal(argspec.var_positional, varargs)
        assert_equal(argspec.named_only, kwonlyargs)
        assert_equal(argspec.var_named, kwargs)

    def _parse(self, in_args):
        return UserKeywordArgumentParser().parse(in_args.split())

    def test_arg_after_defaults(self):
        self._verify_error('${arg1}=default ${arg2}',
                           'Non-default argument after default arguments.')

    def test_multiple_varargs(self):
        for spec in ['@{v1} @{v2}', '@{} @{v}', '@{v} @{}', '@{} @{}']:
            self._verify_error(spec, 'Cannot have multiple varargs.')

    def test_args_after_kwargs(self):
        self._verify_error('&{kws} ${arg}',
                           'Only last argument can be kwargs.')

    def _verify_error(self, in_args, exp_error):
        assert_raises_with_msg(DataError,
                               'Invalid argument specification: ' + exp_error,
                               self._parse, in_args)


if __name__ == '__main__':
    unittest.main()
