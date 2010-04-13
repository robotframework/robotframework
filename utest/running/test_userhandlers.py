import sys
import unittest

from robot.running.userkeyword import UserHandler, EmbeddedArgsTemplate, \
        EmbeddedArgs, UserKeywordArguments
from robot.utils.asserts import *


class HandlerDataMock:

    def __init__(self, name, args=[]):
        self.name = name
        self.args = args
        self.metadata = {}
        self.keywords = []
        self.defaults = []
        self.varargs = None
        self.minargs = 0
        self.maxargs = 0
        self.return_value = None

def EAT(*args):
    return EmbeddedArgsTemplate(HandlerDataMock(*args), 'resource')


class TestEmbeddedArgs(unittest.TestCase):

    def setUp(self):
        self.tmp1 = EAT('User selects ${item} from list')
        self.tmp2 = EAT('${x} * ${y} from "${z}"')

    def test_keyword_has_normal_arguments(self):  
        assert_raises(TypeError, EAT, 'Name has ${args}', ['${norm arg}'])

    def test_no_embedded_args(self):
        assert_raises(TypeError, EAT, 'No embedded args here')

    def test_get_embedded_arg_and_regexp(self):
        assert_equals(self.tmp1.embedded_args, ['${item}'])
        assert_equals(self.tmp1.name_regexp.pattern, 
                      '^User\\ selects\\ (.*?)\\ from\\ list$')
        assert_equals(self.tmp1.name, 'User Selects ${item} From List')
        assert_equals(self.tmp1.longname, 'resource.User Selects ${item} From List')

    def test_get_multiple_embedded_args_and_regexp(self):
        assert_equals(self.tmp2.embedded_args, ['${x}', '${y}', '${z}'])
        assert_equals(self.tmp2.name_regexp.pattern, 
                      '^(.*?)\\ \\*\\ (.*?)\\ from\\ \\"(.*?)\\"$')

    def test_create_handler_when_no_match(self):
        assert_raises(TypeError, EmbeddedArgs, 'Not matching', self.tmp1)

    def test_create_handler_with_one_embedded_arg(self):
        handler = EmbeddedArgs('User selects book from list', self.tmp1)
        assert_equals(handler.embedded_args, [('${item}', 'book')])
        assert_equals(handler.name, 'User selects book from list')
        assert_equals(handler.longname, 'resource.User selects book from list')
        handler = EmbeddedArgs('User selects radio from list', self.tmp1)
        assert_equals(handler.embedded_args, [('${item}', 'radio')])
        assert_equals(handler.name, 'User selects radio from list')
        assert_equals(handler.longname, 'resource.User selects radio from list')

    def test_create_handler_with_many_embedded_args(self):
        handler = EmbeddedArgs('User * book from "list"', self.tmp2)
        assert_equals(handler.embedded_args, 
                      [('${x}', 'User'), ('${y}', 'book'), ('${z}', 'list')])

    def test_create_handler_with_empty_embedded_arg(self):
        handler = EmbeddedArgs('User selects  from list', self.tmp1)
        assert_equals(handler.embedded_args, [('${item}', '')])

    def test_create_handler_with_special_characters_in_embedded_args(self):
        handler = EmbeddedArgs('Janne & Heikki * "enjoy" from """', self.tmp2)
        assert_equals(handler.embedded_args, 
                      [('${x}', 'Janne & Heikki'), ('${y}', '"enjoy"'), ('${z}', '"')])

    def test_embedded_args_without_separators(self):
        template = EAT('This ${does}${not} work so well')
        handler = EmbeddedArgs('This doesnot work so well', template) 
        assert_equals(handler.embedded_args, 
                      [('${does}', ''), ('${not}', 'doesnot')])

    def test_embedded_args_with_separators_in_values(self):
        template = EAT('This ${could} ${work}-${OK}')
        handler = EmbeddedArgs("This doesn't really work---", template) 
        assert_equals(handler.embedded_args, 
                      [('${could}', "doesn't"), ('${work}', 'really work'), ('${OK}', '--')])

    def test_creating_handlers_is_case_insensitive(self):
        handler = EmbeddedArgs('User SELECts book frOm liST', self.tmp1)
        assert_equals(handler.embedded_args, [('${item}', 'book')])
        assert_equals(handler.name, 'User SELECts book frOm liST')
        assert_equals(handler.longname, 'resource.User SELECts book frOm liST')

    def test_embedded_args_handler_has_all_needed_attributes(self):
        normal = UserHandler(HandlerDataMock('My name'), None)
        embedded = EmbeddedArgs('My name', EAT('My ${name}'))
        for attr in dir(normal):
            assert_true(hasattr(embedded, attr), "'%s' missing" % attr)


class _FakeVariables(dict):
    replace_scalar = replace_list = lambda self, args: args


class TestSettingUserKeywordArguments(unittest.TestCase):

    def setUp(self):
        self.variables = _FakeVariables()

    def test_noargs(self):
        ukargs = UserKeywordArguments(argnames=[], defaults=[], vararg=None,
                                      minargs=0, maxargs=0, name='my name')
        ukargs.set_to(self.variables, [])
        self._assert_variables({})

    def test_single_scalar(self):
        self._arguments_for(['${foo}']).set_to(self.variables, ['bar'])
        self._assert_variables({'${foo}': 'bar'})

    def test_multiple_scalars(self):
        self._arguments_for(['${foo}', '${bar}']).set_to(self.variables,
                                                         ['bar', 'quux'])
        self._assert_variables({'${foo}': 'bar', '${bar}': 'quux'})
        self._arguments_for(['${foo}', '${bar}']).set_to(self.variables,
                                                         ['hevonen', 'foox'])
        self._assert_variables({'${foo}': 'hevonen', '${bar}': 'foox'})

    def test_default_values(self):
        self._arguments_for(['${foo}', '${bar}'],
                            ('bar', 'quux')).set_to(self.variables, [])
        self._assert_variables({'${foo}': 'bar', '${bar}': 'quux'})
        self._arguments_for(['${foo}', '${bar}'], ('bar',)).set_to(self.variables,
                                                                   ['kameli'])
        self._assert_variables({'${foo}': 'kameli', '${bar}': 'bar'})

    def test_varargs(self):
        self._arguments_for([], vararg='@{helmet}').set_to(self.variables, [])
        self._assert_variables({'@{helmet}': []})
        self._arguments_for([], vararg='@{helmet}').set_to(self.variables,
                                                           ['kameli', 'hevonen'])
        self._assert_variables({'@{helmet}': ['kameli', 'hevonen']})

    def test_scalar_and_vararg(self):
        self._arguments_for(['${mand}'], vararg='@{varg}').set_to(self.variables, ['muuli'])
        self._assert_variables({'${mand}': 'muuli', '@{varg}': []})

    def test_kwargs(self):
        self._arguments_for(['${a}', '${b}'], ('foo', 'b')).set_to(self.variables,
                                                                   ['b=bar'])
        self._assert_variables({'${a}': 'foo', '${b}': 'bar'})
        args = self._arguments_for(['${a}', '${b}', '${c}'], ('a', 'b', 'c'))
        args.set_to(self.variables, ['a=foo', 'd', 'c=quux'])
        self._assert_variables({'${a}': 'a=foo', '${b}': 'd', '${c}': 'quux'})

    def _arguments_for(self, argnames, defaults=(), vararg=None):
        minargs = len(argnames)-len(defaults)
        maxargs = sys.maxint if vararg else len(argnames)
        return UserKeywordArguments(argnames, defaults, vararg, minargs,
                                    maxargs, 'myname')

    def _assert_variables(self, expected):
        assert_equals(self.variables, expected)


if __name__ == '__main__':
    unittest.main()
