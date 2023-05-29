import unittest
from pathlib import Path

from robot.parsing.suitestructure import IncludedFiles
from robot.utils.asserts import assert_equal


class TestIncludedFiles(unittest.TestCase):

    def test_match_when_no_patterns(self):
        self._test_match()

    def test_match_name(self):
        self._test_match('match.robot')
        self._test_match('no_match.robot', match=False)

    def test_match_path(self):
        self._test_match(Path('match.robot').absolute())
        self._test_match(Path('no_match.robot').absolute(), match=False)

    def test_match_relative_path(self):
        self._test_match('test/match.robot', path='test/match.robot')

    def test_glob_name(self):
        self._test_match('*.robot')
        self._test_match('[mp]???h.robot')
        self._test_match('no_*.robot', match=False)

    def test_glob_path(self):
        self._test_match(Path('*.r?b?t').absolute())
        self._test_match(Path('../*/match.r?b?t').absolute())
        self._test_match(Path('../*/match.r?b?t'))
        self._test_match(Path('*/match.r?b?t'), path='test/match.robot')
        self._test_match(Path('no_*.robot').absolute(), match=False)

    def test_recursive_glob(self):
        self._test_match('x/**/match.robot', path='x/y/z/match.robot')
        self._test_match('x/*/match.robot', path='x/y/z/match.robot', match=False)

    def test_case_normalize(self):
        self._test_match('MATCH.robot')
        self._test_match(Path('match.robot').absolute(), path='MATCH.ROBOT')

    def test_sep_normalize(self):
        self._test_match(str(Path('match.robot').absolute()).replace('\\', '/'))

    def test_directories_are_recursive(self):
        self._test_match('.')
        self._test_match('test', path='test/match.robot')
        self._test_match('test', path='test/x/y/x/match.robot')
        self._test_match('*', path='test/match.robot')

    def _test_match(self, pattern=None, path='match.robot', match=True):
        patterns = [pattern] if pattern else []
        path = Path(path).absolute()
        assert_equal(IncludedFiles(patterns).match(path), match)
        if pattern:
            assert_equal(IncludedFiles(['no', 'match', pattern]).match(path), match)


if __name__ == '__main__':
    unittest.main()
