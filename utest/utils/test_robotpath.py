import unittest
import os

from robot.utils import abspath, normpath, get_link_path
from robot.utils.asserts import assert_equal, assert_true


class TestAbsNormPath(unittest.TestCase):

    def test_abspath(self):
        path = abspath('xxx')
        assert_equal(path, os.path.abspath('xxx'))
        assert_true(isinstance(path, unicode))

    def test_abspath_when_cwd_is_non_ascii(self):
        orig = abspath('.')
        nonasc = u'\xe4'
        os.mkdir(nonasc)
        os.chdir(nonasc)
        try:
            assert_equal(abspath('.'), orig + os.sep + nonasc)
        finally:
            os.chdir('..')
            os.rmdir(nonasc)

    def test_normpath(self):
        for inp, exp in self._get_normpath_inputs():
            assert_equal(normpath(inp), exp, inp)

    def _get_normpath_inputs(self):
        if os.sep == '/':
            return self._get_normpath_inputs_for_posix()
        return self._get_normpath_inputs_for_windows()

    def _get_normpath_inputs_for_posix(self):
        return [('/tmp/', '/tmp'),
                ('/tmp', '/tmp'),
                ('/tmp/foo/..', '/tmp'),
                ('/tmp//', '/tmp'),
                ('/tmp/./', '/tmp'),
                ('/var/../opt/../tmp/.', '/tmp'),
                ('/non/Existing/..', '/non'),
                ('/', '/')]

    def _get_normpath_inputs_for_windows(self):
        inputs = [('c:\\temp', 'c:\\temp'),
                  ('C:\\TEMP\\', 'c:\\temp'),
                  ('c:\\Temp\\foo\..', 'c:\\temp'),
                  ('c:\\temp\\\\', 'c:\\temp'),
                  ('c:\\temp\\.\\', 'c:\\temp'),
                  ('C:\\xxx\\..\\yyy\\..\\temp\\.', 'c:\\temp'),
                  ('c:\\Non\\Existing\\..', 'c:\\non')]
        for x in 'ABCDEFGHIJKLMNOPQRSTUVXYZ':
            base = '%s:\\' % x
            expected = base.lower()
            inputs.append((base, expected))
            inputs.append((base[:2], expected))
            inputs.append((base+'\\foo\\..\\.\\BAR\\\\', expected+'bar'))
        return inputs


class TestGetLinkPath(unittest.TestCase):

    def test_get_link_path(self):
        for basedir, target, expected in self._get_link_path_inputs():
            assert_equal(get_link_path(target, basedir).replace('R:', 'r:'),
                         expected, '%s -> %s' % (target, basedir))

    def test_get_link_path_to_non_existing_path(self):
        assert_equal(get_link_path('/non_existing/foo.txt', '/non_existing/does_not_exist_never.txt'), '../foo.txt')

    def test_get_link_path_with_unicode(self):
        assert_equal(get_link_path(u'\xe4\xf6.txt', ''), '%C3%A4%C3%B6.txt')

    def _get_link_path_inputs(self):
        if os.sep == '/':
            return self._get_link_path_inputs_for_posix()
        return self._get_link_path_inputs_for_windows()

    def _get_link_path_inputs_for_posix(self):
        return [('/tmp/', '/tmp/bar.txt', 'bar.txt'),
                ('/tmp', '/tmp/x/bar.txt', 'x/bar.txt'),
                ('/tmp/', '/tmp/x/y/bar.txt', 'x/y/bar.txt'),
                ('/tmp/', '/tmp/x/y/z/bar.txt', 'x/y/z/bar.txt'),
                ('/tmp', '/x/y/z/bar.txt', '../x/y/z/bar.txt'),
                ('/tmp/', '/x/y/z/bar.txt', '../x/y/z/bar.txt'),
                ('/tmp', '/x/bar.txt', '../x/bar.txt'),
                ('/tmp', '/x/y/z/bar.txt', '../x/y/z/bar.txt'),
                ('/', '/x/bar.txt', 'x/bar.txt'),
                ('/path/to', '/path/to/result_in_same_dir.html',
                 'result_in_same_dir.html'),
                ('/path/to/dir', '/path/to/result_in_parent_dir.html',
                 '../result_in_parent_dir.html'),
                ('/path/to', '/path/to/dir/result_in_sub_dir.html',
                 'dir/result_in_sub_dir.html'),
                ('/commonprefix/sucks/baR', '/commonprefix/sucks/baZ.txt',
                 '../baZ.txt'),
                ('/a/very/long/path', '/no/depth/limitation',
                 '../../../../no/depth/limitation'),
                ('/etc/hosts', '/path/to/existing/file',
                 '../path/to/existing/file'),
                ('/path/to/identity', '/path/to/identity', 'identity')]

    def _get_link_path_inputs_for_windows(self):
        return [('c:\\temp\\', 'c:\\temp\\bar.txt', 'bar.txt'),
                ('c:\\temp', 'c:\\temp\\x\\bar.txt', 'x/bar.txt'),
                ('c:\\temp\\', 'c:\\temp\\x\\y\\bar.txt', 'x/y/bar.txt'),
                ('c:\\temp', 'c:\\temp\\x\\y\\z\\bar.txt', 'x/y/z/bar.txt'),
                ('c:\\temp\\', 'c:\\x\\y\\bar.txt', '../x/y/bar.txt'),
                ('c:\\temp', 'c:\\x\\y\\bar.txt', '../x/y/bar.txt'),
                ('c:\\temp', 'c:\\x\\bar.txt', '../x/bar.txt'),
                ('c:\\temp', 'c:\\x\\y\\z\\bar.txt', '../x/y/z/bar.txt'),
                ('c:\\temp\\', 'r:\\x\\y\\bar.txt', 'file:///r:/x/y/bar.txt'),
                ('c:\\', 'c:\\x\\bar.txt', 'x/bar.txt'),
                ('c:\\path\\to', 'c:\\path\\to\\result_in_same_dir.html',
                 'result_in_same_dir.html'),
                ('c:\\path\\to\\dir', 'c:\\path\\to\\result_in_parent.dir',
                 '../result_in_parent.dir'),
                ('c:\\path\\to', 'c:\\path\\to\\dir\\result_in_sub_dir.html',
                 'dir/result_in_sub_dir.html'),
                ('c:\\commonprefix\\sucks\\baR',
                 'c:\\commonprefix\\sucks\\baZ.txt', '../baZ.txt'),
                ('c:\\a\\very\\long\\path', 'c:\\no\\depth\\limitation',
                 '../../../../no/depth/limitation'),
                ('c:\\windows\\explorer.exe',
                 'c:\\windows\\path\\to\\existing\\file',
                 'path/to/existing/file'),
                ('c:\\path\\2\\identity', 'c:\\path\\2\\identity', 'identity')]
