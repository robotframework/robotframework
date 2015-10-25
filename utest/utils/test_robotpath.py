import unittest
import os
import os.path

from robot.utils import abspath, normpath, get_link_path, WINDOWS, PY3
from robot.utils.robotpath import CASE_INSENSITIVE_FILESYSTEM
from robot.utils.asserts import assert_equal, assert_true


if PY3:
    unicode = str


class TestAbspathNormpath(unittest.TestCase):

    def test_abspath(self):
        for inp, exp in self._get_inputs():
            exp = os.path.abspath(exp)
            path = abspath(inp)
            assert_equal(path, exp, inp)
            assert_true(isinstance(path, unicode), inp)
            exp = exp.lower() if CASE_INSENSITIVE_FILESYSTEM else exp
            path = abspath(inp, case_normalize=True)
            assert_equal(path, exp, inp)
            assert_true(isinstance(path, unicode), inp)

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

    if WINDOWS:
        unc_path = r'\\server\D$\dir\.\f1\..\\f2'
        unc_exp = r'\\server\D$\dir\f2'

        def test_unc_path(self):
            assert_equal(abspath(self.unc_path), self.unc_exp)

        def test_unc_path_when_chdir_is_root(self):
            orig = abspath('.')
            os.chdir('\\')
            try:
                assert_equal(abspath(self.unc_path), self.unc_exp)
            finally:
                os.chdir(orig)

    def test_normpath(self):
        for inp, exp in self._get_inputs():
            path = normpath(inp)
            assert_equal(path, exp, inp)
            assert_true(isinstance(path, unicode), inp)
            exp = exp.lower() if CASE_INSENSITIVE_FILESYSTEM else exp
            path = normpath(inp, case_normalize=True)
            assert_equal(path, exp, inp)
            assert_true(isinstance(path, unicode), inp)

    def _get_inputs(self):
        inputs = self._windows_inputs if WINDOWS else self._posix_inputs
        for inp, exp in inputs():
            yield inp, exp
            if inp not in ['', os.sep]:
                for ext in [os.sep, os.sep+'.', os.sep+'.'+os.sep]:
                    yield inp + ext, exp
            if inp.endswith(os.sep):
                for ext in ['.', '.'+os.sep, '.'+os.sep+'.']:
                    yield inp + ext, exp
                yield inp + 'foo' + os.sep + '..', exp

    def _posix_inputs(self):
        return [('/tmp/', '/tmp'),
                ('/var/../opt/../tmp/.', '/tmp'),
                ('/non/Existing/..', '/non'),
                ('/', '/')] + self._generic_inputs()

    def _windows_inputs(self):
        inputs = [('c:\\temp', 'c:\\temp'),
                  ('C:\\TEMP\\', 'C:\\TEMP'),
                  ('C:\\xxx\\..\\yyy\\..\\temp\\.', 'C:\\temp'),
                  ('c:\\Non\\Existing\\..', 'c:\\Non')]
        for x in 'ABCDEFGHIJKLMNOPQRSTUVXYZ':
            base = '%s:\\' % x
            inputs.append((base, base))
            inputs.append((base.lower(), base.lower()))
            inputs.append((base[:2], base))
            inputs.append((base[:2].lower(), base.lower()))
            inputs.append((base+'\\foo\\..\\.\\BAR\\\\', base+'BAR'))
        inputs += [(inp.replace('/', '\\'), exp) for inp, exp in inputs]
        for inp, exp in self._generic_inputs():
            exp = exp.replace('/', '\\')
            inputs.extend([(inp, exp), (inp.replace('/', '\\'), exp)])
        return inputs

    def _generic_inputs(self):
        return [('', '.'),
                ('.', '.'),
                ('./', '.'),
                ('..', '..'),
                ('../', '..'),
                ('../..', '../..'),
                ('foo', 'foo'),
                ('foo/bar', 'foo/bar'),
                (u'\xe4', u'\xe4'),
                (u'\xe4/\xf6', u'\xe4/\xf6'),
                ('./foo', 'foo'),
                ('foo/.', 'foo'),
                ('foo/..', '.'),
                ('foo/../bar', 'bar'),
                ('foo/bar/zap/..', 'foo/bar')]


class TestGetLinkPath(unittest.TestCase):

    def test_get_link_path(self):
        inputs = self._posix_inputs if os.sep == '/' else self._windows_inputs
        for basedir, target, expected in inputs():
            assert_equal(get_link_path(target, basedir).replace('R:', 'r:'),
                         expected, '%s -> %s' % (target, basedir))

    def test_get_link_path_to_non_existing_path(self):
        assert_equal(get_link_path('/non-ex/foo.txt', '/non-ex/nothing_here.txt'),
                     '../foo.txt')

    def test_get_non_ascii_link_path(self):
        assert_equal(get_link_path(u'\xe4\xf6.txt', ''), '%C3%A4%C3%B6.txt')

    def _posix_inputs(self):
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

    def _windows_inputs(self):
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


if __name__ == '__main__':
    unittest.main()
