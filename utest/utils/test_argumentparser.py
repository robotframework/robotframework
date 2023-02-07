import os
import unittest
import warnings

from robot.utils.argumentparser import ArgumentParser
from robot.utils.asserts import (assert_equal, assert_raises,
                                 assert_raises_with_msg, assert_true)
from robot.errors import Information, DataError, FrameworkError
from robot.version import get_full_version


USAGE = """Example Tool -- Stuff before hyphens is considered name

Usage:  robot.py [options] datafile

Version: <VERSION>

Options:
  -d --reportdir dir        Explanation
  -r --reportfile file      This explanation continues ............... 78
       ........... to multiple lines.
       Next line is totally empty.

  -E --escape what:with *      Line below has nothing after '*'. Next line has
          nothing after value and next nothing after option name
  -v --variable name:value *
  -N --name name
  -t -T --toggle   Something
  -h -? --help
  --version  Explanation

  -z   No long option so not an option line.
  --z  No long option here either
  this line doesn't start with a '-' so not an --optionline
  -\\-option     escaped 1
  -o -\\-option  escaped 2
          --ignored  options cannot be this far
          --ignored

* denotes options that can be set multiple times
"""

USAGE2 = """Just Name Here
usage:  robot.py [options] arg1 arg2

options:
  -v --variable name=value
  -x --var-able name=v1,v2   Explanation
  -3 --42
  --help
"""


class TestArgumentParserInit(unittest.TestCase):

    def setUp(self):
        self.ap = ArgumentParser(USAGE)

    def assert_long_opts(self, expected, ap=None):
        expected += ['no' + e for e in expected if not e.endswith('=')]
        long_opts = (ap or self.ap)._long_opts
        assert_equal(sorted(long_opts), sorted(expected))

    def assert_short_opts(self, expected, ap=None):
        assert_equal((ap or self.ap)._short_opts, expected)

    def assert_multi_opts(self, expected, ap=None):
        assert_equal((ap or self.ap)._multi_opts, expected)

    def assert_flag_opts(self, expected, ap=None):
        assert_equal((ap or self.ap)._flag_opts, expected)

    def test_short_options(self):
        self.assert_short_opts('d:r:E:v:N:tTh?')

    def test_long_options(self):
        self.assert_long_opts(['reportdir=', 'reportfile=', 'escape=',
                               'variable=', 'name=', 'toggle', 'help',
                               'version'])

    def test_multi_options(self):
        self.assert_multi_opts(['escape', 'variable'])

    def test_flag_options(self):
        self.assert_flag_opts(['toggle', 'help', 'version'])

    def test_options_must_be_indented_by_1_to_four_spaces(self):
        ap = ArgumentParser('''Name
1234567890
--notin  this option is not indented at all and thus ignored
 --opt1
    --opt2        This option is 4 spaces from left -> included
    -o --opt3 argument  It doesn't matter how far the option gets.
     --notopt     This option is 5 spaces from left -> not included
     -i --ignored
                     --not-in-either
    --included  back in four space indentation''')
        self.assert_long_opts(['opt1', 'opt2', 'opt3=', 'included'], ap)

    def test_case_insensitive_long_options(self):
        ap = ArgumentParser(' -f --foo\n -B --BAR\n')
        self.assert_short_opts('fB', ap)
        self.assert_long_opts(['foo', 'bar'], ap)

    def test_long_options_with_hyphens(self):
        ap = ArgumentParser(' -f --f-o-o\n -B --bar--\n')
        self.assert_short_opts('fB', ap)
        self.assert_long_opts(['foo', 'bar'], ap)

    def test_same_option_multiple_times(self):
        for usage in [' --foo\n --foo\n',
                      ' --foo\n -f --Foo\n',
                      ' -x --foo xxx\n -y --Foo yyy\n',
                      ' -f --foo\n -f --bar\n']:
            assert_raises(FrameworkError, ArgumentParser, usage)
        ap = ArgumentParser(' -f --foo\n -F --bar\n')
        self.assert_short_opts('fF', ap)
        self.assert_long_opts(['foo', 'bar'], ap)

    def test_same_option_multiple_times_with_no_prefix(self):
        for usage in [' --foo\n --nofoo\n',
                      ' --nofoo\n --foo\n'
                      ' --nose size\n --se\n']:
            assert_raises(FrameworkError, ArgumentParser, usage)
        ap = ArgumentParser(' --foo value\n --nofoo value\n')
        self.assert_long_opts(['foo=', 'nofoo='], ap)


class TestArgumentParserParseArgs(unittest.TestCase):

    def setUp(self):
        self.ap = ArgumentParser(USAGE)

    def test_missing_argument_file_throws_data_error(self):
        inargs = '--argumentfile missing_argument_file_that_really_is_not_there.txt'.split()
        self.assertRaises(DataError, self.ap.parse_args, inargs)

    def test_single_options(self):
        inargs = '-d reports --reportfile reps.html -T arg'.split()
        opts, args = self.ap.parse_args(inargs)
        assert_equal(opts, {'reportdir': 'reports', 'reportfile': 'reps.html',
                            'escape': [], 'variable': [], 'name': None,
                            'toggle': True})

    def test_multi_options(self):
        inargs = '-v a:1 -v b:2 --name my_name --variable c:3 arg'.split()
        opts, args = self.ap.parse_args(inargs)
        assert_equal(opts, {'variable': ['a:1', 'b:2', 'c:3'], 'escape': [],
                            'name': 'my_name', 'reportdir': None,
                            'reportfile': None, 'toggle': None})
        assert_equal(args, ['arg'])

    def test_flag_options(self):
        for inargs, exp in [('', None),
                            ('--name whatever', None),
                            ('--toggle', True),
                            ('-T', True),
                            ('--toggle --name whatever -t', True),
                            ('-t -T --toggle', True),
                            ('--notoggle', False),
                            ('--notoggle --name xxx --notoggle', False),
                            ('--toggle --notoggle', False),
                            ('-t -t -T -T --toggle -T --notoggle', False),
                            ('--notoggle --toggle --notoggle', False),
                            ('--notoggle --toggle', True),
                            ('--notoggle --notoggle -T', True)]:
            opts, args = self.ap.parse_args(inargs.split() + ['arg'])
            assert_equal(opts['toggle'], exp, inargs)
            assert_equal(args, ['arg'])

    def test_flag_option_with_no_prefix(self):
        ap = ArgumentParser(' -S --nostatusrc\n --name name')
        for inargs, exp in [('', None),
                            ('--name whatever', None),
                            ('--nostatusrc', False),
                            ('-S', False),
                            ('--nostatusrc -S --nostatusrc -S -S', False),
                            ('--statusrc', True),
                            ('--statusrc --statusrc -S', False),
                            ('--nostatusrc --nostatusrc -S --statusrc', True)]:
            opts, args = ap.parse_args(inargs.split() + ['arg'])
            assert_equal(opts['statusrc'], exp, inargs)
            assert_equal(args, ['arg'])

    def test_single_option_multiple_times(self):
        for inargs in ['--name Foo -N Bar arg',
                       '-N Zap --name Foo --name Bar arg',
                       '-N 1 -N 2 -N 3 -t --variable foo -N 4 --name Bar arg']:
            opts, args = self.ap.parse_args(inargs.split())
            assert_equal(opts['name'], 'Bar')
            assert_equal(args, ['arg'])

    def test_case_insensitive_long_options(self):
        opts, args = self.ap.parse_args('--VarIable X:y --TOGGLE arg'.split())
        assert_equal(opts['variable'], ['X:y'])
        assert_equal(opts['toggle'], True)
        assert_equal(args, ['arg'])

    def test_case_insensitive_long_options_with_equal_sign(self):
        opts, args = self.ap.parse_args('--VariAble=X:y --VARIABLE=ZzZ'.split())
        assert_equal(opts['variable'], ['X:y', 'ZzZ'])
        assert_equal(args, [])

    def test_long_options_with_hyphens(self):
        opts, args = self.ap.parse_args('--var-i-a--ble x-y ----toggle---- arg'.split())
        assert_equal(opts['variable'], ['x-y'])
        assert_equal(opts['toggle'], True)
        assert_equal(args, ['arg'])

    def test_long_options_with_hyphens_with_equal_sign(self):
        opts, args = self.ap.parse_args('--var-i-a--ble=x-y ----variable----=--z--'.split())
        assert_equal(opts['variable'], ['x-y', '--z--'])
        assert_equal(args, [])

    def test_long_options_with_hyphens_only(self):
        args = '-----=value1'.split()
        assert_raises(DataError, self.ap.parse_args, args)

    def test_split_pythonpath(self):
        ap = ArgumentParser('ignored')
        data = [(['path'], ['path']),
                (['path1','path2'], ['path1','path2']),
                (['path1:path2'], ['path1','path2']),
                (['p1:p2:p3','p4','.'], ['p1','p2','p3','p4','.'])]
        if os.sep == '\\':
            data += [(['c:\\path'], ['c:\\path']),
                     (['c:\\path','d:\\path'], ['c:\\path','d:\\path']),
                     (['c:\\path:d:\\path'], ['c:\\path','d:\\path']),
                     (['c:/path:x:yy:d:\\path','c','.','x:/xxx'],
                      ['c:\\path', 'x', 'yy', 'd:\\path', 'c', '.', 'x:\\xxx'])]
        for inp, exp in data:
            assert_equal(ap._split_pythonpath(inp), exp)

    def test_get_pythonpath(self):
        ap = ArgumentParser('ignored')
        p1 = os.path.abspath('.')
        p2 = os.path.abspath('..')
        assert_equal(ap._get_pythonpath(p1), [p1])
        assert_equal(ap._get_pythonpath([p1,p2]), [p1,p2])
        assert_equal(ap._get_pythonpath([p1 + ':' + p2]), [p1,p2])
        assert_true(p1 in ap._get_pythonpath(os.path.join(p2,'*')))

    def test_arguments_are_globbed(self):
        _, args = self.ap.parse_args([__file__.replace('test_', '?????')])
        assert_equal(args, [__file__])
        # Needed to ensure that the globbed directory contains files
        globexpr = os.path.join(os.path.dirname(__file__), '*')
        _, args = self.ap.parse_args([globexpr])
        assert_true(len(args) > 1)

    def test_arguments_with_glob_patterns_arent_removed_if_they_dont_match(self):
        _, args = self.ap.parse_args(['*.non.existing', 'non.ex.??'])
        assert_equal(args, ['*.non.existing', 'non.ex.??'])

    def test_special_options_are_removed(self):
        ap = ArgumentParser('''Usage:
 -h --help
 -v --version
 --Argument-File path
 --option
''')
        opts, args = ap.parse_args(['--option'])
        assert_equal(opts, {'option': True})

    def test_special_options_can_be_turned_to_normal_options(self):
        ap = ArgumentParser('''Usage:
 -h --help
 -v --version
 --argumentfile path
''', auto_help=False, auto_version=False, auto_argumentfile=False)
        opts, args = ap.parse_args(['--help', '-v', '--arg', 'xxx'])
        assert_equal(opts, {'help': True, 'version': True, 'argumentfile': 'xxx'})

    def test_auto_pythonpath_is_deprecated(self):
        with warnings.catch_warnings(record=True) as w:
            ArgumentParser('-x', auto_pythonpath=False)
        assert_equal(str(w[0].message),
                     "ArgumentParser option 'auto_pythonpath' is deprecated "
                     "since Robot Framework 5.0.")

    def test_non_list_args(self):
        ap = ArgumentParser('''Options:
 -t --toggle
 -v --value value
 -m --multi multi *
''')
        opts, args = ap.parse_args(())
        assert_equal(opts, {'toggle': None,
                             'value': None,
                             'multi': []})
        assert_equal(args, [])
        opts, args = ap.parse_args(('-t', '-v', 'xxx', '-m', '1', '-m2', 'arg'))
        assert_equal(opts, {'toggle': True,
                             'value': 'xxx',
                             'multi': ['1', '2']})
        assert_equal(args, ['arg'])


class TestDefaultsFromEnvironmentVariables(unittest.TestCase):

    def setUp(self):
        os.environ['ROBOT_TEST_OPTIONS'] = '-t --value default -m1 --multi=2'
        self.ap = ArgumentParser('''Options:
 -t --toggle
 -v --value value
 -m --multi multi *
''', env_options='ROBOT_TEST_OPTIONS')

    def tearDown(self):
        os.environ.pop('ROBOT_TEST_OPTIONS')

    def test_flag(self):
        opts, args = self.ap.parse_args([])
        assert_equal(opts['toggle'], True)
        opts, args = self.ap.parse_args(['--toggle'])
        assert_equal(opts['toggle'], True)
        opts, args = self.ap.parse_args(['--notoggle'])
        assert_equal(opts['toggle'], False)

    def test_value(self):
        opts, args = self.ap.parse_args([])
        assert_equal(opts['value'], 'default')
        opts, args = self.ap.parse_args(['--value', 'given'])
        assert_equal(opts['value'], 'given')

    def test_multi_value(self):
        opts, args = self.ap.parse_args([])
        assert_equal(opts['multi'], ['1', '2'])
        opts, args = self.ap.parse_args(['-m3', '--multi', '4'])
        assert_equal(opts['multi'], ['1', '2', '3', '4'])

    def test_arguments(self):
        os.environ['ROBOT_TEST_OPTIONS'] = '-o opt arg1 arg2'
        ap = ArgumentParser('Usage:\n -o --opt value',
                            env_options='ROBOT_TEST_OPTIONS')
        opts, args = ap.parse_args([])
        assert_equal(opts['opt'], 'opt')
        assert_equal(args, ['arg1', 'arg2'])

    def test_environment_variable_not_set(self):
        ap = ArgumentParser('Usage:\n -o --opt value', env_options='NOT_SET')
        opts, args = ap.parse_args(['arg'])
        assert_equal(opts['opt'], None)
        assert_equal(args, ['arg'])


class TestArgumentValidation(unittest.TestCase):

    def test_check_args_with_correct_args(self):
        for arg_limits in [None, (1, 1), 1, (1,)]:
            ap = ArgumentParser(USAGE, arg_limits=arg_limits)
            assert_equal(ap.parse_args(['hello'])[1], ['hello'])

    def test_default_validation(self):
        ap = ArgumentParser(USAGE)
        for args in [(), ('1',), ('m', 'a', 'n', 'y')]:
            assert_equal(ap.parse_args(args)[1], list(args))

    def test_check_args_with_wrong_number_of_args(self):
        for limits in [1, (1, 1), (1, 2)]:
            ap = ArgumentParser('usage', arg_limits=limits)
            for args in [(), ('arg1', 'arg2', 'arg3')]:
                assert_raises(DataError, ap.parse_args, args)

    def test_check_variable_number_of_args(self):
        ap = ArgumentParser('usage:  robot.py [options] args', arg_limits=(1,))
        ap.parse_args(['one_is_ok'])
        ap.parse_args(['two', 'ok'])
        ap.parse_args(['this', 'should', 'also', 'work', '!'])
        assert_raises_with_msg(DataError, "Expected at least 1 argument, got 0.",
                               ap.parse_args, [])

    def test_argument_range(self):
        ap = ArgumentParser('usage:  test.py [options] args', arg_limits=(2,4))
        ap.parse_args(['1', '2'])
        ap.parse_args(['1', '2', '3', '4'])
        assert_raises_with_msg(DataError, "Expected 2 to 4 arguments, got 1.",
                               ap.parse_args, ['one is not enough'])

    def test_no_arguments(self):
        ap = ArgumentParser('usage:  test.py [options]', arg_limits=(0, 0))
        ap.parse_args([])
        assert_raises_with_msg(DataError, "Expected 0 arguments, got 2.",
                               ap.parse_args, ['1', '2'])

    def test_custom_validator_fails(self):
        def validate(options, args):
            raise AssertionError
        ap = ArgumentParser(USAGE2, validator=validate)
        assert_raises(AssertionError, ap.parse_args, [])

    def test_custom_validator_return_value(self):
        def validate(options, args):
            return options, [a.upper() for a in args]
        ap = ArgumentParser(USAGE2, validator=validate)
        opts, args = ap.parse_args(['-v', 'value', 'inp1', 'inp2'])
        assert_equal(opts['variable'], 'value')
        assert_equal(args, ['INP1', 'INP2'])


class TestPrintHelpAndVersion(unittest.TestCase):

    def setUp(self):
        self.ap = ArgumentParser(USAGE, version='1.0 alpha')
        self.ap2 = ArgumentParser(USAGE2)

    def test_print_help(self):
        assert_raises_with_msg(Information, USAGE2,
                               self.ap2.parse_args, ['--help'])

    def test_name_is_got_from_first_line_of_the_usage(self):
        assert_equal(self.ap.name, 'Example Tool')
        assert_equal(self.ap2.name, 'Just Name Here')

    def test_name_and_version_can_be_given(self):
        ap = ArgumentParser(USAGE, name='Kakkonen', version='2')
        assert_equal(ap.name, 'Kakkonen')
        assert_equal(ap.version, '2')

    def test_print_version(self):
        assert_raises_with_msg(Information, 'Example Tool 1.0 alpha',
                               self.ap.parse_args, ['--version'])

    def test_print_version_when_version_not_set(self):
        ap = ArgumentParser(' --version', name='Kekkonen')
        msg = assert_raises(Information, ap.parse_args, ['--version'])
        assert_equal(str(msg), 'Kekkonen %s' % get_full_version())

    def test_version_is_replaced_in_help(self):
        assert_raises_with_msg(Information, USAGE.replace('<VERSION>', '1.0 alpha'),
                               self.ap.parse_args, ['--help'])


if __name__ == "__main__":
    unittest.main()
