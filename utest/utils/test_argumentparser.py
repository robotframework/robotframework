import unittest
import sys
import os

from robot.utils.argumentparser import *
from robot.utils.asserts import *
from robot.errors import *

usage = """
usage:  robot.py [options] datafile

options:
  -d  --reportdir dir        Explanation
  -r  --reportfile file      This explanation continues ............... 78
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

* denotes options that can be set multiple times
"""

usage2 = """
usage:  robot.py [options] arg1 arg2

options:
  -v     --variable name=value  
  -x     --var-able name=v1,v2   Explanation 
"""


class TestArgumentParserInit(unittest.TestCase):

    def setUp(self):
        self.ap = ArgumentParser(usage)

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
        self.ap = ArgumentParser(usage)

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

    def test_non_ascii_chars(self):
        ap = ArgumentParser(usage2)
        inargs = '-x foo=bar --variable a=1,2,3 arg1 arg2'.split()
        exp_opts = { 'var-able':'foo=bar', 'variable':'a=1,2,3' }
        exp_args = [ 'arg1', 'arg2' ]
        opts, args = ap.parse_args(inargs)
        assert_equals(opts, exp_opts)
        assert_equals(args, exp_args)
 
    def test_check_args_with_correct_args(self):
        for args in [ ('hello',), ('hello world',) ]:
            self.ap.check_args(args)
    
    def test_check_args_with_wrong_number_of_args(self):
        for args in [ (), ('arg1','arg2','arg3') ]:
            assert_raises(DataError, self.ap.check_args, args)
    
    def test_unescape_options(self):
        cli = '--escape quot:Q -E space:SP -E lt:LT -E gt:GT ' \
                + '-N QQQLTmySPfineSPnameGTQQQ sourceSPwithSPspaces'
        opts, args = self.ap.parse_args(cli.split(), unescape='escape');
        assert_equals(opts['name'], '"""<my fine name>"""')
        assert_equals(opts['escape'], ['quot:Q','space:SP','lt:LT','gt:GT'])
        assert_equals(args, ['source with spaces'])

    def test_split_pythonpath(self):
        ap = ArgumentParser('')
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
        ap = ArgumentParser('')
        p1 = os.path.abspath('.')
        p2 = os.path.abspath('..')
        assert_equals(ap._get_pythonpath(p1), [p1])
        assert_equals(ap._get_pythonpath([p1,p2]), [p1,p2])
        assert_equals(ap._get_pythonpath([p1 + ':' + p2]), [p1,p2])
        assert_true(p1 in ap._get_pythonpath(os.path.join(p2,'*')))


if __name__ == "__main__":
    unittest.main()
