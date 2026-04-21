import unittest

from robot.running.builder.parsers import MarkdownParser
from robot.utils.asserts import assert_equal


class FakeFileReader:

    def __init__(self, text):
        self._lines = text.splitlines(keepends=True)

    def readlines(self):
        return self._lines


class TestReadMarkdownData(unittest.TestCase):

    def assert_no_data(self, md):
        self._assert(md, "")

    def assert_data(self, md, expected="data\n"):
        self._assert(md, expected)

    def _assert(self, md, expected):
        parser = MarkdownParser()
        actual = parser._read_markdown_data(FakeFileReader(md))
        assert_equal(actual, expected)

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
            "data 1\n\ndata 2\n",
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
"""
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
            "```\n\n~~~\n",
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


if __name__ == "__main__":
    unittest.main()
