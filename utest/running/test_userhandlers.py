import unittest

from robot.errors import DataError
from robot.model import Keywords
from robot.running.userkeyword import EmbeddedArgumentsHandler
from robot.running.arguments import EmbeddedArguments, UserKeywordArgumentParser
from robot.utils.asserts import assert_equal, assert_true, assert_raises


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
        self.metadata = {}
        self.keywords = Keywords()
        self.defaults = []
        self.varargs = None
        self.minargs = 0
        self.maxargs = 0
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
        assert_equal(self.tmp2.embedded_name.pattern,
                     '^(.*?)\\ \\*\\ (.*?)\\ from\\ \\"(.*?)\\"$')

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

    def test_one_arg(self):
        self._verify('${arg1}', ['arg1',])

    def test_one_vararg(self):
        self._verify('@{varargs}', exp_varargs='varargs')

    def test_one_default(self):
        self._verify('${arg1} ${arg2}=default @{varargs}',
                     ['arg1', 'arg2'], ['default'], 'varargs')

    def test_one_empty_default(self):
        self._verify('${arg1} ${arg2}= @{varargs}',
                     ['arg1', 'arg2'], [''], 'varargs')

    def test_many_defaults(self):
        self._verify('${arg1}=default1 ${arg2}=default2 ${arg3}=default3',
                     ['arg1', 'arg2', 'arg3'],
                     ['default1', 'default2', 'default3'])

    def _verify(self, in_args, exp_args=[], exp_defaults=[], exp_varargs=None):
        argspec = self._parse(in_args)
        assert_equal(argspec.positional, exp_args)
        assert_equal(argspec.defaults, exp_defaults)
        assert_equal(argspec.varargs, exp_varargs)

    def _parse(self, in_args):
        return UserKeywordArgumentParser().parse(in_args.split())

    def test_many_varargs_raises(self):
        assert_raises(DataError, self._parse, '@{varargs} @{varargs2}')

    def test_args_after_varargs_raises(self):
        assert_raises(DataError, self._parse, '@{varargs} ${arg1}')

    def test_get_defaults_before_args_raises(self):
        assert_raises(DataError, self._parse, '${args1}=default ${arg2}')


if __name__ == '__main__':
    unittest.main()
