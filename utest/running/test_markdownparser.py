import os
import tempfile
import unittest
from pathlib import Path

from robot.parsing import get_model, ModelVisitor
from robot.running import TestSuite
from robot.running.builder.parsers import MarkdownParser
from robot.utils.asserts import assert_equal


class FakeFileReader:

    def __init__(self, text):
        self._lines = text.splitlines(keepends=True)

    def readlines(self):
        return self._lines


class TokenCollector(ModelVisitor):

    def __init__(self):
        self.tokens = []

    def visit_Statement(self, node):
        self.tokens.extend((t.value, t.lineno, t.col_offset) for t in node.tokens)


class TestReadMarkdownData(unittest.TestCase):

    def assert_no_data(self, md):
        self._assert(md, "")

    def assert_data(self, md, expected="data\n", offsets=None):
        self._assert(md, expected, offsets)

    def _assert(self, md, expected, offsets=None):
        parser = MarkdownParser()
        data, actual_offsets = parser._read_markdown_data(FakeFileReader(md))
        lines = data.splitlines(keepends=True)
        assert_equal(len(lines), len(md.splitlines()))
        assert_equal("".join(line for line in lines if line.strip()), expected)
        assert_equal(actual_offsets, offsets or {})

    def test_empty(self):
        self.assert_no_data("")

    def test_no_blocks(self):
        self.assert_no_data(
            """
# Title

Some text.
"""
        )

    def test_single_robotframework_block(self):
        self.assert_data(
            """
```robotframework
data
```
"""
        )

    def test_single_robot_block(self):
        self.assert_data(
            """
```robot
data
```
"""
        )

    def test_unrecognized_block(self):
        self.assert_no_data(
            """
```python
def foo():
    pass
```

```
no data
```
"""
        )

    def test_multiple_blocks(self):
        self.assert_data(
            """
```robotframework
data 1
```

```
no data
```

```robot
data 2
```
""",
            "data 1\ndata 2\n",
        )

    def test_text_outside_blocks_ignored(self):
        self.assert_data(
            """
Ignored
```robotframework
data
```
Also ignored
"""
        )

    def test_fence_with_leading_whitespace(self):
        self.assert_data(
            """
  ```robotframework
data
  ```
"""
        )

    def test_leading_whitespace_must_not_match(self):
        self.assert_data(
            """
                 ```robotframework
           data
     ```
""",
            offsets={3: 11},
        )

    def test_whitespace_before_language(self):
        self.assert_data(
            """
```       robotframework
data
```
"""
        )

    def test_content_after_language(self):
        self.assert_data(
            """
~~~robot start=3
data
~~~
"""
        )

    def test_no_trailing_newline(self):
        self.assert_data(
            """
```robotframework
data
```"""
        )

    def test_empty_block(self):
        self.assert_no_data(
            """
```robotframework
```
""",
        )

    def test_unclosed_block(self):
        self.assert_data(
            """
```robotframework
data
"""
        )

    def test_dedent(self):
        self.assert_data(
            """
- An example:
  ```robotframework
  left
      indent

          more indent
  ```
""",
            """\
left
    indent
        more indent
""",
            offsets={4: 2, 5: 2, 7: 2},
        )

    def test_tilde_fence(self):
        self.assert_data(
            """
~~~robotframework
data
~~~
"""
        )

    def test_fence_styles_must_match(self):
        self.assert_data(
            """
~~~robotframework
```
~~~

```robot
~~~
```
""",
            "```\n~~~\n",
        )

    def test_longer_fence(self):
        self.assert_data(
            """
``````robot
data
``````
"""
        )

    def test_longer_close_fence(self):
        self.assert_data(
            """
```robot
data
``````````
"""
        )

    def test_too_short_open_fence(self):
        self.assert_no_data(
            """
``robot
no data
```
"""
        )

    def test_too_short_close_fence(self):
        self.assert_data(
            """
```robot
data
``
more?
""",
            "data\n``\nmore?\n",
        )


class TestLineAndColumnNumbers(unittest.TestCase):
    path = Path(os.getenv("TEMPDIR") or tempfile.gettempdir(), "test_markdown.robot.md")
    data = """\
# Title

Text.

- List item:

  ```robotframework
  *** Test Cases ***
  Test
      Log    Hello!
  ```

```robot
*** Keywords ***
Keyword
    No Operation
```
"""

    @classmethod
    def setUpClass(cls):
        cls.path.write_text(cls.data, encoding="UTF-8")

    @classmethod
    def tearDownClass(cls):
        cls.path.unlink()

    def test_parsing_model(self):
        model = MarkdownParser()._get_model(get_model, self.path)
        collector = TokenCollector()
        collector.visit(model)
        assert_equal(
            collector.tokens,
            [
                ("*** Test Cases ***", 8, 2),
                ("Test", 9, 2),
                ("Log", 10, 6),
                ("Hello!", 10, 13),
                ("*** Keywords ***", 14, 0),
                ("Keyword", 15, 0),
                ("No Operation", 16, 4),
            ],
        )

    def test_running_model(self):
        suite = TestSuite.from_file_system(self.path)
        assert_equal(suite.tests[0].lineno, 9)
        assert_equal(suite.tests[0].body[0].lineno, 10)
        assert_equal(suite.resource.keywords[0].lineno, 15)


if __name__ == "__main__":
    unittest.main()
