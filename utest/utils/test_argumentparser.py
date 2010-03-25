import unittest
import os

from robot.utils.argumentparser import ArgumentParser
from robot.utils.asserts import *
from robot.errors import Information, DataError, FrameworkError


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
"""


class TestArgumentParserInit(unittest.TestCase):

    def setUp(self):
        self.ap = ArgumentParser(USAGE)

    def test_short_options(self):
        assert_equals(self.ap._short_opts, 'd:r:E:v:N:h?')

    def test_long_options(self):
        expected = [ 'reportdir=', 'reportfile=', 'escape=', 'variable=',
                     'name=', 'help', 'version' ]
        assert_equals(self.ap._long_opts, expected)

    def test_multi_options(self):
        assert_equals(self.ap._multi_opts, ['escape','variable'])

    def test_toggle_options(self):
        assert_equals(self.ap._toggle_opts, ['help','version'])

    def test_options_over_4_spaces_from_left_are_ignored(self):
        assert_equals(ArgumentParser('''Name
1234567890
--opt1
    --opt2        This option is 4 spaces from left -> included
    -o --opt3 argument  It doesn't matter how far the option gets.
     --notopt     This option is 5 spaces from left -> not included
     -i --ignored
                     --not-in-either
        ''')._long_opts, ['opt1', 'opt2', 'opt3='])

    def test_case_insensitive_long_options(self):
        ap = ArgumentParser(' -f --foo\n -B --BAR\n')
        assert_equals(ap._short_opts, 'fB')
        assert_equals(ap._long_opts, ['foo','bar'])

    def test_same_option_multiple_times(self):
        for my_usage in [ ' --foo\n --foo\n',
                         ' --foo\n -f --Foo\n',
                         ' -x --foo xxx\n -y --Foo yyy\n',
                         ' -f --foo\n -f --bar\n' ]:
            assert_raises(FrameworkError, ArgumentParser, my_usage)
        ap = ArgumentParser(' -f --foo\n -F --bar\n')
        assert_equals(ap._short_opts, 'fF')
        assert_equals(ap._long_opts, ['foo','bar'])


class TestArgumentParserParseArgs(unittest.TestCase):

    def setUp(self):
        self.ap = ArgumentParser(USAGE)

    def test_single_options(self):
        inargs = '-d reports --reportfile report.html -? arg'.split()
        exp_opts = {'reportdir':'reports', 'reportfile':'report.html',
                    'variable':[], 'name':None, 'escape' : [],
                    'help':True, 'version':False }
        exp_args = [ 'arg' ]
        opts, args = self.ap.parse_args(inargs)
        assert_equals(opts, exp_opts)
        assert_equals(args, exp_args)

    def test_multi_options(self):
        inargs = '-v a:1 -v b:2 --name my_name --variable c:3 arg'.split()
        exp_opts = {'variable':['a:1','b:2','c:3'], 'name':'my_name',
                    'reportdir':None, 'reportfile':None, 'escape' : [],
                    'help':False, 'version':False }
        exp_args = [ 'arg' ]
        opts, args = self.ap.parse_args(inargs)
        assert_equals(opts, exp_opts)
        assert_equals(args, exp_args)

    def test_toggle_options(self):
        for inargs, exp in [ ('arg', False),
                             ('--help arg', True),
                             ('--help --name whatever -h arg', False),
                             ('-? -h --help arg', True) ]:
            opts, args = self.ap.parse_args(inargs.split())
            assert_equals(opts['help'], exp)
            assert_equals(args, ['arg'])

    def test_single_option_multiple_times(self):
        for inargs in [ '--name Foo -N Bar arg',
                        '-N Zap --name Foo --name Bar arg',
                        '-N 1 -N 2 -N 3 -h --variable foo -N 4 --name Bar arg' ]:
            opts, args = self.ap.parse_args(inargs.split())
            assert_equals(opts['name'], 'Bar')
            assert_equals(args, ['arg'])

    def test_case_insensitive_long_options(self):
        opts, args = self.ap.parse_args('--EsCape X:y --HELP arg'.split())
        assert_equals(opts['escape'], ['X:y'])
        assert_equals(opts['help'], True)
        assert_equals(args, ['arg'])

    def test_case_insensitive_long_options_with_equal_sign(self):
        opts, args = self.ap.parse_args('--EsCape=X:y --escAPE=ZZ'.split())
        assert_equals(opts['escape'], ['X:y', 'ZZ'])
        assert_equals(args, [])

    def test_non_ascii_chars(self):
        ap = ArgumentParser(USAGE2)
        inargs = '-x foo=bar --variable a=1,2,3 arg1 arg2'.split()
        exp_opts = {'var-able':'foo=bar', 'variable':'a=1,2,3', '42': False}
        exp_args = ['arg1', 'arg2']
        opts, args = ap.parse_args(inargs)
        assert_equals(opts, exp_opts)
        assert_equals(args, exp_args)

    def test_check_args_with_correct_args(self):
        for args in [ ('hello',), ('hello world',) ]:
            self.ap.parse_args(args, check_args=True)

    def test_check_args_with_wrong_number_of_args(self):
        for args in [ (), ('arg1','arg2','arg3') ]:
            assert_raises(DataError, self.ap._check_args, args)

    def test_check_variable_number_of_args(self):
        ap = ArgumentParser('usage:  robot.py [options] args')
        ap.parse_args(['one_is_ok'], check_args=True)
        ap.parse_args(['two', 'ok'], check_args=True)
        ap.parse_args(['this', 'should', 'also', 'work', '!'], check_args=True)
        assert_raises_with_msg(DataError, "Expected at least 1 argument, got 0.",
                               ap._check_args, [])

    def test_arg_limits_to_constructor(self):
        ap = ArgumentParser('usage:  test.py [options] args', arg_limits=(2,4))
        assert_raises_with_msg(DataError, "Expected 2 to 4 arguments, got 1.",
                               ap._check_args, ['one is not enough'])

    def test_reading_args_from_usage_when_it_has_just_options(self):
        ap = ArgumentParser('usage:  test.py [options]')
        ap.parse_args([], check_args=True)
        assert_raises_with_msg(DataError, "Expected 0 arguments, got 2.",
                               ap._check_args, ['1', '2'])

    def test_check_args_fails_when_no_args_specified(self):
        assert_raises(FrameworkError, ArgumentParser('test').parse_args,
                      [], check_args=True)


    def test_unescape_options(self):
        cli = '--escape quot:Q -E space:SP -E lt:LT -E gt:GT ' \
                + '-N QQQLTmySPfineSPnameGTQQQ sourceSPwithSPspaces'
        opts, args = self.ap.parse_args(cli.split(), unescape='escape');
        assert_equals(opts['name'], '"""<my fine name>"""')
        assert_equals(opts['escape'], ['quot:Q','space:SP','lt:LT','gt:GT'])
        assert_equals(args, ['source with spaces'])

    def test_split_pythonpath(self):
        ap = ArgumentParser('ignored')
        data = [ (['path'], ['path']),
                 (['path1','path2'], ['path1','path2']),
                 (['path1:path2'], ['path1','path2']),
                 (['p1:p2:p3','p4','.'], ['p1','p2','p3','p4','.']) ]
        if os.sep == '\\':
            data += [ (['c:\\path'], ['c:\\path']),
                      (['c:\\path','d:\\path'], ['c:\\path','d:\\path']),
                      (['c:\\path:d:\\path'], ['c:\\path','d:\\path']),
                      (['c:/path:x:yy:d:\\path','c','.','x:/xxx'],
                       ['c:\\path', 'x', 'yy', 'd:\\path', 'c', '.', 'x:\\xxx']) ]
        for inp, exp in data:
            assert_equals(ap._split_pythonpath(inp), exp)

    def test_get_pythonpath(self):
        ap = ArgumentParser('ignored')
        p1 = os.path.abspath('.')
        p2 = os.path.abspath('..')
        assert_equals(ap._get_pythonpath(p1), [p1])
        assert_equals(ap._get_pythonpath([p1,p2]), [p1,p2])
        assert_equals(ap._get_pythonpath([p1 + ':' + p2]), [p1,p2])
        assert_true(p1 in ap._get_pythonpath(os.path.join(p2,'*')))

    def test_arguments_are_globbed(self):
        _, args = self.ap.parse_args([__file__.replace('test_', '?????')])
        assert_equals(args, [__file__])
        # Needed to ensure that the globbed directory contains files
        globexpr = os.path.join(os.path.dirname(__file__), '*')
        _, args = self.ap.parse_args([globexpr])
        assert_true(len(args) > 1)

    def test_arguments_with_glob_patterns_arent_removed_if_they_dont_match(self):
        _, args = self.ap.parse_args(['*.non.existing', 'non.ex.??'])
        assert_equals(args, ['*.non.existing', 'non.ex.??'])


class TestPrintHelpAndVersion(unittest.TestCase):

    def setUp(self):
        self.ap = ArgumentParser(USAGE, version='1.0 alpha')
        self.ap2 = ArgumentParser(USAGE2)

    def test_print_help(self):
        assert_raises_with_msg(Information, USAGE2,
                               self.ap2.parse_args, ['--42'], help='42')

    def test_name_is_got_from_first_line_of_the_usage(self):
        assert_equals(self.ap._name, 'Example Tool')
        assert_equals(self.ap2._name, 'Just Name Here')

    def test_print_version(self):
        assert_raises_with_msg(Information, 'Example Tool 1.0 alpha',
                               self.ap.parse_args, ['--version'], version='version')

    def test_print_version_when_version_not_set(self):
        assert_raises(FrameworkError, self.ap2.parse_args, ['--42', '-x a'], version='42')

    def test_version_is_replaced_in_help(self):
        assert_raises_with_msg(Information, USAGE.replace('<VERSION>', '1.0 alpha'),
                               self.ap.parse_args, ['--help'], help='help')

    def test_escapes_are_replaced_in_help(self):
        usage = """Name
 --escape x:y      blaa blaa .............................................. end
                   <-----------------------ESCAPES---------------------------->
                   -- next line --
 --he"""
        expected = """Name
 --escape x:y      blaa blaa .............................................. end
                   Available escapes:
                   amp (&), apos ('), at (@), bslash (\), colon (:), comma (,),
                   curly1 ({), curly2 (}), dollar ($), exclam (!), gt (>), hash
                   (#), lt (<), paren1 ((), paren2 ()), percent (%), pipe (|),
                   quest (?), quot ("), semic (;), slash (/), space ( ),
                   square1 ([), square2 (]), star (*)
                   -- next line --
 --he"""
        assert_raises_with_msg(Information, expected,
                               ArgumentParser(usage).parse_args, ['--he'], help='he')


if __name__ == "__main__":
    unittest.main()
