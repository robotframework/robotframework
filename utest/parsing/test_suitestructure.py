import tempfile
import unittest
from pathlib import Path

from robot.parsing.suitestructure import IncludedFiles, SuiteStructureBuilder
from robot.utils.asserts import assert_equal


class TestIncludedFiles(unittest.TestCase):

    def test_match_when_no_patterns(self):
        self._test_match()

    def test_match_name(self):
        self._test_match("match.robot")
        self._test_match("no_match.robot", match=False)

    def test_match_path(self):
        self._test_match(Path("match.robot").absolute())
        self._test_match(Path("no_match.robot").absolute(), match=False)

    def test_match_relative_path(self):
        self._test_match("test/match.robot", path="test/match.robot")

    def test_glob_name(self):
        self._test_match("*.robot")
        self._test_match("[mp]???h.robot")
        self._test_match("no_*.robot", match=False)

    def test_glob_path(self):
        self._test_match(Path("*.r?b?t").absolute())
        self._test_match(Path("../*/match.r?b?t").absolute())
        self._test_match(Path("../*/match.r?b?t"))
        self._test_match(Path("*/match.r?b?t"), path="test/match.robot")
        self._test_match(Path("no_*.robot").absolute(), match=False)

    def test_recursive_glob(self):
        self._test_match("x/**/match.robot", path="x/y/z/match.robot")
        self._test_match("x/*/match.robot", path="x/y/z/match.robot", match=False)

    def test_case_normalize(self):
        self._test_match("MATCH.robot")
        self._test_match(Path("match.robot").absolute(), path="MATCH.ROBOT")

    def test_sep_normalize(self):
        self._test_match(str(Path("match.robot").absolute()).replace("\\", "/"))

    def test_directories_are_recursive(self):
        self._test_match(".")
        self._test_match("test", path="test/match.robot")
        self._test_match("test", path="test/x/y/x/match.robot")
        self._test_match("*", path="test/match.robot")

    def _test_match(self, pattern=None, path="match.robot", match=True):
        patterns = [pattern] if pattern else []
        path = Path(path).absolute()
        assert_equal(IncludedFiles(patterns).match(path), match)
        if pattern:
            assert_equal(IncludedFiles(["no", "match", pattern]).match(path), match)


class TestSuiteStructureBuilder(unittest.TestCase):

    def test_is_init_file(self):
        builder = SuiteStructureBuilder()
        with tempfile.TemporaryDirectory() as td:
            temp_dir = Path(td)
            for name in (
                "__init__.robot",
                "__init__.robot.md",
                "__init__.robot.rst",
                "__init__.rbt",
                "__INIT__.ROBOT",
                "__INIT__.ROBOT.MD",
                "__INIT__.ROBOT.RST",
            ):
                file_path = temp_dir / name
                file_path.touch()
                assert_equal(
                    builder._is_init_file(file_path),
                    True,
                    f"Expected {name} to be init file",
                )

            for name in (
                "__init__.md",
                "__init__.rst",
                "__init__.txt",
                "test.robot",
                "__init__.foo.robot",
                "not__init__.robot",
            ):
                file_path = temp_dir / name
                file_path.touch()
                assert_equal(
                    builder._is_init_file(file_path),
                    False,
                    f"Expected {name} not to be init file",
                )

    def test_is_init_file_with_custom_extensions(self):
        builder = SuiteStructureBuilder(extensions=[".custom.md", ".txt"])
        with tempfile.TemporaryDirectory() as td:
            temp_dir = Path(td)
            init_custom = temp_dir / "__init__.custom.md"
            init_custom.touch()
            assert_equal(builder._is_init_file(init_custom), True)

            init_txt = temp_dir / "__init__.txt"
            init_txt.touch()
            assert_equal(builder._is_init_file(init_txt), True)

            init_robot = temp_dir / "__init__.robot"
            init_robot.touch()
            assert_equal(builder._is_init_file(init_robot), False)


if __name__ == "__main__":
    unittest.main()
