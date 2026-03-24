import unittest

from robot.running.builder.parsers import MarkdownParser
from robot.utils.asserts import assert_equal


class FakeFileReader:
    def __init__(self, text):
        self._lines = text.splitlines(keepends=True)

    def readlines(self):
        return self._lines


def read(text):
    parser = MarkdownParser()
    return parser._read_markdown_data(FakeFileReader(text))


class TestReadMarkdownData(unittest.TestCase):

    def test_empty_file(self):
        # (empty file)
        assert_equal(read(""), "")

    def test_no_robot_blocks(self):
        # # Title
        #
        # Some text.
        assert_equal(read("# Title\n\nSome text.\n"), "")

    def test_single_robotframework_block(self):
        # ```robotframework
        # *** Test Cases ***
        # My Test    Log    Hello, RF!
        # ```
        md = (
            "```robotframework\n*** Test Cases ***\nMy Test    Log    Hello, RF!\n```\n"
        )
        assert_equal(read(md), "*** Test Cases ***\nMy Test    Log    Hello, RF!")

    def test_single_robot_block(self):
        # ```robot
        # *** Test Cases ***
        # My Test    Log    Hello, Robot!
        # ```
        md = "```robot\n*** Test Cases ***\nMy Test    Log    Hello, Robot!\n```\n"
        assert_equal(read(md), "*** Test Cases ***\nMy Test    Log    Hello, Robot!")

    def test_non_robot_code_block_ignored(self):
        # ```python
        # def foo(): pass
        # ```
        assert_equal(read("```python\ndef foo(): pass\n```\n"), "")

    def test_multiple_blocks_separated_by_empty_line(self):
        # ```robotframework
        # *** Settings ***
        # Selenium Library
        # ```
        #
        # ```robotframework
        # *** Test Cases ***
        # T    Log    x
        # ```
        md = (
            "```robotframework\n*** Settings ***\nSelenium Library\n```\n"
            "\n"
            "```robotframework\n*** Test Cases ***\nT    Log    x\n```\n"
        )
        result = read(md)
        assert_equal(
            result,
            "*** Settings ***\nSelenium Library\n\n*** Test Cases ***\nT    Log    x",
        )

    def test_text_outside_blocks_ignored(self):
        # Ignored
        # ```robotframework
        # *** Test Cases ***
        # ```
        # Also ignored
        md = "Ignored\n```robotframework\n*** Test Cases ***\n```\nAlso ignored\n"
        assert_equal(read(md), "*** Test Cases ***")

    def test_block_fence_with_leading_whitespace_recognized(self):
        #   ```robotframework
        # *** Test Cases ***
        #   ```
        md = "  ```robotframework\n*** Test Cases ***\n  ```\n"
        assert_equal(read(md), "*** Test Cases ***")

    def test_partial_fence_not_recognized(self):
        # ```robot-extension
        # *** Test Cases ***
        # ```
        md = "```robot-extension\n*** Test Cases ***\n```\n"
        assert_equal(read(md), "")

    def test_no_trailing_newline_after_last_block(self):
        # ```robotframework
        # *** Test Cases ***
        # ``` (no trailing newline)
        md = "```robotframework\n*** Test Cases ***\n```"
        assert_equal(read(md), "*** Test Cases ***")

    def test_empty_block(self):
        # ```robotframework
        # ```
        md = "```robotframework\n```\n"
        assert_equal(read(md), "")

    def test_unclosed_block_includes_content_until_eof(self):
        # ```robotframework
        # *** Test Cases ***
        # My Test    Log    Hello, Robot!  (no closing fence)
        md = "```robotframework\n*** Test Cases ***\nMy Test    Log    Hello, Robot!"
        assert_equal(read(md), "*** Test Cases ***\nMy Test    Log    Hello, Robot!")


if __name__ == "__main__":
    unittest.main()
