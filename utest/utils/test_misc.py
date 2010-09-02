import os
import unittest
import sys

from robot.utils.asserts import assert_equals
from robot import utils
if utils.is_jython:
    import JavaExceptions

from robot.utils.misc import *


class TestMiscUtils(unittest.TestCase):

    def test_seq2str(self):
        for seq, expected in [((), ''), ([], ''), (set(), ''),
                              (['One'], "'One'"),
                              (['1', '2'], "'1' and '2'"),
                              (['a', 'b', 'c', 'd'], "'a', 'b', 'c' and 'd'")]:
            assert_equals(seq2str(seq), expected)

    def test_get_link_path(self):
        if os.sep == '/':
            inputs = [
                ( '/tmp/', '/tmp/bar.txt', 'bar.txt' ),
                ( '/tmp', '/tmp/x/bar.txt', 'x/bar.txt' ),
                ( '/tmp/', '/tmp/x/y/bar.txt', 'x/y/bar.txt' ),
                ( '/tmp/', '/tmp/x/y/z/bar.txt', 'x/y/z/bar.txt' ),
                ( '/tmp', '/x/y/z/bar.txt', '../x/y/z/bar.txt' ),
                ( '/tmp/', '/x/y/z/bar.txt', '../x/y/z/bar.txt' ),
                ( '/tmp', '/x/bar.txt', '../x/bar.txt' ),
                ( '/tmp', '/x/y/z/bar.txt', '../x/y/z/bar.txt' ),
                ( '/', '/x/bar.txt', 'x/bar.txt' ),
                ( '/path/to', '/path/to/result_in_same_dir.html', 'result_in_same_dir.html' ),
                ( '/path/to/dir', '/path/to/result_in_parent_dir.html', '../result_in_parent_dir.html' ),
                ( '/path/to', '/path/to/dir/result_in_sub_dir.html', 'dir/result_in_sub_dir.html' ),
                ( '/commonprefix/sucks/baR', '/commonprefix/sucks/baZ.txt', '../baZ.txt' ),
                ( '/a/very/long/path', '/no/depth/limitation', '../../../../no/depth/limitation' ),
                ( '/etc/hosts', '/path/to/existing/file', '../path/to/existing/file' ),
                ( '/path/to/identity', '/path/to/identity', 'identity' ),
            ]
        else:
            inputs = [
                ( 'c:\\temp\\', 'c:\\temp\\bar.txt', 'bar.txt' ),
                ( 'c:\\temp', 'c:\\temp\\x\\bar.txt', 'x/bar.txt' ),
                ( 'c:\\temp\\', 'c:\\temp\\x\\y\\bar.txt', 'x/y/bar.txt' ),
                ( 'c:\\temp', 'c:\\temp\\x\\y\\z\\bar.txt', 'x/y/z/bar.txt' ),
                ( 'c:\\temp\\', 'c:\\x\\y\\bar.txt', '../x/y/bar.txt' ),
                ( 'c:\\temp', 'c:\\x\\y\\bar.txt', '../x/y/bar.txt' ),
                ( 'c:\\temp', 'c:\\x\\bar.txt', '../x/bar.txt' ),
                ( 'c:\\temp', 'c:\\x\\y\\z\\bar.txt', '../x/y/z/bar.txt' ),
                ( 'c:\\temp\\', 'r:\\x\\y\\bar.txt', 'file:///r:/x/y/bar.txt' ),
                ( 'c:\\', 'c:\\x\\bar.txt', 'x/bar.txt' ),
                ( 'c:\\path\\to', 'c:\\path\\to\\result_in_same_dir.html', 'result_in_same_dir.html' ),
                ( 'c:\\path\\to\\dir', 'c:\\path\\to\\result_in_parent_dir.html', '../result_in_parent_dir.html' ),
                ( 'c:\\path\\to', 'c:\\path\\to\\dir\\result_in_sub_dir.html', 'dir/result_in_sub_dir.html' ),
                ( 'c:\\commonprefix\\sucks\\baR', 'c:\\commonprefix\\sucks\\baZ.txt', '../baz.txt' ),
                ( 'c:\\a\\very\\long\\path', 'c:\\no\\depth\\limitation', '../../../../no/depth/limitation' ),
                ( 'c:\\boot.ini', 'c:\\path\\to\\existing\\file', 'path/to/existing/file' ),
                ( 'c:\\path\\to\\identity', 'c:\\path\\to\\identity', 'identity' ),
            ]
        import robot.utils.normalizing
        for basedir, target, expected in inputs:
            if robot.utils.normalizing._CASE_INSENSITIVE_FILESYSTEM :
                expected = expected.lower()
            assert_equals(get_link_path(target, basedir).replace('R:', 'r:'), expected,
                         '%s -> %s' % (target, basedir))

    def test_get_link_path_with_unicode(self):
        assert_equals(get_link_path(u'\xe4\xf6.txt', ''),'%C3%A4%C3%B6.txt')


    def test_printable_name(self):
        for inp, exp in [ ('simple', 'Simple'),
                          ('ALLCAPS', 'ALLCAPS'),
                          ('name with spaces', 'Name With Spaces'),
                          ('more   spaces', 'More Spaces'),
                          ('Cases AND spaces', 'Cases AND Spaces'),
                          ('under_Score_name', 'Under_Score_name'),
                          ('camelCaseName', 'CamelCaseName'),
                          ('with89numbers', 'With89numbers'),
                          ('with 89 numbers', 'With 89 Numbers'),
                          ('', '') ]:
            assert_equals(printable_name(inp), exp)

    def test_printable_name_with_code_style(self):
        for inp, exp in [ ('simple', 'Simple'),
                          ('ALLCAPS', 'ALLCAPS'),
                          ('under_score_name', 'Under Score Name'),
                          ('under_score and spaces', 'Under Score And Spaces'),
                          ('miXed_CAPS_nAMe', 'MiXed CAPS NAMe'),
                          ('camelCaseName', 'Camel Case Name'),
                          ('camelCaseWithDigit1', 'Camel Case With Digit 1'),
                          ('name42WithNumbers666', 'Name 42 With Numbers 666'),
                          ('12more34numbers', '12 More 34 Numbers'),
                          ('mixedCAPSCamelName', 'Mixed CAPS Camel Name'),
                          ('foo-bar', 'Foo-bar'),
                          ('','') ]:
            assert_equals(printable_name(inp, code_style=True), exp)


if __name__ == "__main__":
    unittest.main()
