import sys
import unittest

from robot.errors import DataError
from robot.running import UserKeyword, ResourceFile, TestCase
from robot.running.arguments import EmbeddedArguments, UserKeywordArgumentParser
from robot.utils.asserts import assert_equal, assert_true, assert_raises_with_msg


class TestBind(unittest.TestCase):

    def setUp(self):
        self.res = ResourceFile()
        self.tc = TestCase()
        self.kw1 = UserKeyword('Hello', ['${arg}'], 'doc', ['tags'], '1s', 42, self.res)
        self.kw2 = self.kw1.bind(self.tc.body.create_keyword())

    def test_data(self):
        kw = self.kw2
        assert_equal(kw.name, 'Hello')
        assert_equal(kw.args.positional, ('arg',))
        assert_equal(kw.doc, 'doc')
        assert_equal(kw.tags, ['tags'])
        assert_equal(kw.timeout, '1s')
        assert_equal(kw.lineno, 42)

    def test_owner_and_parent(self):
        kw = self.kw2
        assert_equal(kw.owner, self.res)
        assert_equal(kw.parent, self.tc)

    def test_data_is_copied(self):
        kw1, kw2 = self.kw1, self.kw2
        kw2.name = kw2.doc = 'New'
        kw2.args.positional_or_named = ('new', 'args')
        kw2.args.defaults['args'] = 'xxx'
        kw2.tags.add('new')
        kw2.lineno = 666
        assert_equal(kw1.name, 'Hello')
        assert_equal(kw1.args.positional, ('arg',))
        assert_equal(kw1.args.defaults, {})
        assert_equal(kw1.doc, 'doc')
        assert_equal(kw1.tags, ['tags'])
        assert_equal(kw1.timeout, '1s')
        assert_equal(kw1.lineno, 42)
        assert_equal(kw1.owner, self.res)


class TestEmbeddedArgs(unittest.TestCase):

    def setUp(self):
        self.kw1 = UserKeyword('User selects ${item} from list')
        self.kw2 = UserKeyword('${x} * ${y} from "${z}"')

    def test_truthy(self):
        assert_true(EmbeddedArguments.from_name('${Yes} embedded args here'))
        assert_true(not EmbeddedArguments.from_name('No embedded args here'))

    def test_get_embedded_arg_and_regexp(self):
        assert_equal(self.kw1.embedded.args, ('item',))
        assert_equal(self.kw1.embedded.name.pattern,
                     '^User\\ selects\\ (.*?)\\ from\\ list$')
        assert_equal(self.kw1.name, 'User selects ${item} from list')

    def test_get_multiple_embedded_args_and_regexp(self):
        assert_equal(self.kw2.embedded.args, ('x', 'y', 'z'))
        assert_equal(self.kw2.embedded.name.pattern,
                     '^(.*?)\\ \\*\\ (.*?)\\ from\\ "(.*?)"$')

    def test_create_runner_with_one_embedded_arg(self):
        runner = self.kw1.create_runner('User selects book from list')
        assert_equal(runner.name, 'User selects book from list')
        assert_equal(runner.embedded_args, ('book',))
        self.kw1.owner = ResourceFile(source='xxx.resource')
        runner = self.kw1.create_runner('User selects radio from list')
        assert_equal(runner.name, 'User selects radio from list')
        assert_equal(runner.embedded_args, ('radio',))

    def test_create_runner_with_many_embedded_args(self):
        runner = self.kw2.create_runner('User * book from "list"')
        assert_equal(runner.embedded_args, ('User', 'book', 'list'))

    def test_create_runner_with_empty_embedded_arg(self):
        runner = self.kw1.create_runner('User selects  from list')
        assert_equal(runner.embedded_args, ('',))

    def test_create_runner_with_special_characters_in_embedded_args(self):
        runner = self.kw2.create_runner('Janne & Heikki * "enjoy" from """')
        assert_equal(runner.embedded_args, ('Janne & Heikki', '"enjoy"', '"'))

    def test_embedded_args_without_separators(self):
        kw = UserKeyword('This ${does}${not} work so well')
        runner = kw.create_runner('This doesnot work so well')
        assert_equal(runner.embedded_args, ('', 'doesnot'))

    def test_embedded_args_with_separators_in_values(self):
        kw = UserKeyword('This ${could} ${work}-${OK}')
        runner = kw.create_runner("This doesn't really work---")
        assert_equal(runner.embedded_args, ("doesn't", 'really work', '--'))

    def test_creating_runners_is_case_insensitive(self):
        runner = self.kw1.create_runner('User SELECts book frOm liST')
        assert_equal(runner.embedded_args, ('book',))
        assert_equal(runner.name, 'User SELECts book frOm liST')


class TestGetArgSpec(unittest.TestCase):

    def test_no_args(self):
        self._verify('')

    def test_args(self):
        self._verify('${arg1}', ('arg1',))
        self._verify('${a1} ${a2}', ('a1', 'a2'))

    def test_defaults(self):
        self._verify('${arg1} ${arg2}=default @{varargs}',
                     positional=['arg1', 'arg2'],
                     defaults={'arg2': 'default'},
                     var_positional='varargs')
        self._verify('${arg1} ${arg2}= @{varargs}',
                     positional=['arg1', 'arg2'],
                     defaults={'arg2': ''},
                     var_positional='varargs')
        self._verify('${arg1}=d1 ${arg2}=d2 ${arg3}=d3',
                     positional=['arg1', 'arg2', 'arg3'],
                     defaults={'arg1': 'd1', 'arg2': 'd2', 'arg3': 'd3'})

    def test_vararg(self):
        self._verify('@{varargs}', var_positional='varargs')
        self._verify('${arg} @{varargs}', ['arg'], var_positional='varargs')

    def test_kwonly(self):
        self._verify('@{} ${ko1} ${ko2}',
                     named_only=['ko1', 'ko2'])
        self._verify('@{vars} ${ko1} ${ko2}',
                     var_positional='vars',
                     named_only=['ko1', 'ko2'])

    def test_kwonly_with_defaults(self):
        self._verify('@{} ${ko1} ${ko2}=xxx',
                     named_only=['ko1', 'ko2'],
                     defaults={'ko2': 'xxx'})
        self._verify('@{} ${ko1}=xxx ${ko2}',
                     named_only=['ko1', 'ko2'],
                     defaults={'ko1': 'xxx'})
        self._verify('@{v} ${ko1}=foo ${ko2} ${ko3}=',
                     var_positional='v',
                     named_only=['ko1', 'ko2', 'ko3'],
                     defaults={'ko1': 'foo', 'ko3': ''})

    def test_kwargs(self):
        self._verify('&{kwargs}',
                     var_named='kwargs')
        self._verify('${arg} &{kwargs}',
                     positional=['arg'],
                     var_named='kwargs')
        self._verify('@{} ${arg} &{kwargs}',
                     named_only=['arg'],
                     var_named='kwargs')
        self._verify('${a1} ${a2}=ad @{vars} ${k1} ${k2}=kd &{kws}',
                     positional=['a1', 'a2'],
                     var_positional='vars',
                     named_only=['k1', 'k2'],
                     defaults={'a2': 'ad', 'k2': 'kd'},
                     var_named='kws')

    def _verify(self, in_args, positional=(), var_positional=None,
                named_only=(), var_named=None, defaults=None):
        spec = self._parse(in_args)
        assert_equal(spec.positional, tuple(positional))
        assert_equal(spec.var_positional, var_positional)
        assert_equal(spec.named_only, tuple(named_only))
        assert_equal(spec.var_named, var_named)
        assert_equal(spec.defaults, defaults or {})

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
