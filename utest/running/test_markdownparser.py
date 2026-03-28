import unittest

from robot.running.builder.parsers import MarkdownParser
from robot.utils.asserts import assert_equal


class FakeFileReader:
    def __init__(self, text):
        self._lines = text.splitlines(keepends=True)

    def readlines(self):
        return self._lines


def _read(text):
    parser = MarkdownParser()
    return parser._read_markdown_data(FakeFileReader(text))


class TestReadMarkdownData(unittest.TestCase):

    def test_empty_file(self):
        # (empty file)
        assert_equal(_read(""), "")

    def test_no_robot_blocks(self):
        # # Title
        #
        # Some text.
        assert_equal(_read("# Title\n\nSome text.\n"), "")

    def test_single_robotframework_block(self):
        # ```robotframework
        # *** Test Cases ***
        # My Test    Log    Hello, RF!
        # ```
        md = (
            "```robotframework\n*** Test Cases ***\nMy Test    Log    Hello, RF!\n```\n"
        )
        assert_equal(_read(md), "*** Test Cases ***\nMy Test    Log    Hello, RF!\n")

    def test_single_robot_block(self):
        # ```robot
        # *** Test Cases ***
        # My Test    Log    Hello, Robot!
        # ```
        md = "```robot\n*** Test Cases ***\nMy Test    Log    Hello, Robot!\n```\n"
        assert_equal(_read(md), "*** Test Cases ***\nMy Test    Log    Hello, Robot!\n")

    def test_non_robot_code_block_ignored(self):
        # ```python
        # def foo(): pass
        # ```
        assert_equal(_read("```python\ndef foo(): pass\n```\n"), "")

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
            ""
            "```robotframework\n*** Test Cases ***\nT    Log    x\n```\n"
        )
        result = _read(md)
        assert_equal(
            result,
            "*** Settings ***\nSelenium Library\n"
            "\n"
            "*** Test Cases ***\nT    Log    x\n",
        )

    def test_text_outside_blocks_ignored(self):
        # Ignored
        # ```robotframework
        # *** Test Cases ***
        # ```
        # Also ignored
        md = "Ignored\n```robotframework\n*** Test Cases ***\n```\nAlso ignored\n"
        assert_equal(_read(md), "*** Test Cases ***\n")

    def test_block_fence_with_leading_whitespace_recognized(self):
        #   ```robotframework
        # *** Test Cases ***
        #   ```
        md = "  ```robotframework\n*** Test Cases ***\n  ```\n"
        assert_equal(_read(md), "*** Test Cases ***\n")

    def test_wrong_fence_not_recognized(self):
        # ```robot-extension
        # *** Test Cases ***
        # ```
        md = "```robot-extension\n*** Test Cases ***\n```\n"
        assert_equal(_read(md), "")

    def test_no_trailing_newline_after_last_block(self):
        # ```robotframework
        # *** Test Cases ***
        # ``` (no trailing newline)
        md = "```robotframework\n*** Test Cases ***\n```"
        assert_equal(_read(md), "*** Test Cases ***\n")

    def test_empty_block(self):
        # ```robotframework
        # ```
        md = "```robotframework\n```\n"
        assert_equal(_read(md), "")

    def test_unclosed_block_includes_content_until_eof(self):
        # ```robotframework
        # *** Test Cases ***
        # My Test    Log    Hello, Robot!  (no closing fence)
        md = "```robotframework\n*** Test Cases ***\nMy Test    Log    Hello, Robot!"
        assert_equal(_read(md), "*** Test Cases ***\nMy Test    Log    Hello, Robot!")

    def test_indented_block_content_is_dedented(self):
        # - A list item:
        #   ```robotframework
        #   *** Test Cases ***
        #   My Test    Log    Hello
        #   ```
        md = (
            "- A list item:\n"
            "  ```robotframework\n"
            "  *** Test Cases ***\n"
            "  My Test    Log    Hello\n"
            "  ```\n"
        )
        assert_equal(_read(md), "*** Test Cases ***\nMy Test    Log    Hello\n")

    def test_two_indented_blocks_content_is_dedented(self):
        # - First item:
        #   ```robotframework
        #   *** Settings ***
        #   Library    Collections
        #   ```
        #
        # - Second item:
        #   ```robotframework
        #   *** Test Cases ***
        #   My Test    Log    Hello
        #   ```
        md = (
            "- First item:\n"
            "  ```robotframework\n"
            "  *** Settings ***\n"
            "  Library    Collections\n"
            "  ```\n"
            "\n"
            "- Second item:\n"
            "  ```robotframework\n"
            "  *** Test Cases ***\n"
            "  My Test    Log    Hello\n"
            "  ```\n"
        )
        assert_equal(
            _read(md),
            "*** Settings ***\nLibrary    Collections\n"
            "\n"
            "*** Test Cases ***\nMy Test    Log    Hello\n",
        )

    def test_tilde_fence_blocks(self):
        # ~~~robotframework
        # *** Test Cases ***
        # My Test    Log    Tilde Fence
        # ~~~
        md = "~~~robotframework\n*** Test Cases ***\nMy Test    Log    Tilde Fence\n~~~\n"
        assert_equal(_read(md), "*** Test Cases ***\nMy Test    Log    Tilde Fence\n")

    def test_longer_fence(self):
        # ``````robot
        # *** Test Cases ***
        # My Test    Log    Longer Fence
        # ``````
        md = "``````robot\n*** Test Cases ***\nMy Test    Log    Longer Fence\n``````\n"
        assert_equal(_read(md), "*** Test Cases ***\nMy Test    Log    Longer Fence\n")

    def test_longer_closure_fence(self):
        # ```robot
        # *** Test Cases ***
        # My Test    Log    Longer Fence
        # ````
        md = "```robot\n*** Test Cases ***\nMy Test    Log    Longer Fence\n````\n"
        assert_equal(_read(md), "*** Test Cases ***\nMy Test    Log    Longer Fence\n")

    def test_fence_with_info_string(self):
        # ~~~robot start=3
        # *** Test Cases ***
        # My Test    Log    Info String
        # ~~~
        md = (
            "~~~robot start=3\n*** Test Cases ***\nMy Test    Log    Info String\n~~~\n"
        )
        assert_equal(_read(md), "*** Test Cases ***\nMy Test    Log    Info String\n")


if __name__ == "__main__":
    unittest.main()
