import unittest
from dataclasses import dataclass

import yaml

from robot.running.docstringparser import parse_docstring
from robot.utils.asserts import assert_equal


@dataclass
class Expected:
    doc: str
    args: "dict[str, str]"
    returns: str = ""


class DocstringParsing(unittest.TestCase):

    def verify(self, data):
        tests_run = False
        for name, docstring, expected in self.get_data(data):
            with self.subTest(msg=name):
                parsed = parse_docstring(docstring)
                assert_equal(parsed.doc, expected.doc, formatter=repr)
                assert_equal(parsed.returns, expected.returns, formatter=repr)
                assert_equal(list(parsed.args), list(expected.args))
                for key in parsed.args:
                    assert_equal(parsed.args[key], expected.args[key], formatter=repr)
            tests_run = True
        if not tests_run:
            raise ValueError("No tests found in data")

    def get_data(self, data):
        for test in data.split("\n## ")[1:]:
            name, test = test.lstrip().split("\n", 1)
            docstring, expected = test.split("- - -\n")
            expected = yaml.safe_load(expected) or {}
            expected = Expected(
                expected.get("doc", "").rstrip(),
                {k: v.rstrip() for k, v in expected.get("args", {}).items()},
                expected.get("returns", "").rstrip(),
            )
            yield name, docstring, expected

    def test_sections_and_boundaries(self):
        self.verify(
            """
## Empty
- - -

## Documentation only
Doc

Some more documentation
- - -
doc: |
    Doc

    Some more documentation

## Arguments only
Args:
    name: Documentation
- - -
args:
    name: Documentation

## Returns only
Returns:
    The result value.
- - -
returns: The result value.

## All sections
Doc

Args:
    name: Documentation

Bit more documentation

Returns:
    The result value.

Even more documentation
- - -
doc: |
    Doc

    Bit more documentation

    Even more documentation
args:
    name: Documentation
returns:
    The result value.

## Empty sections
Args:

Returns:
- - -

## Single space indentation ends section
Args:
    name: Documentation
 Part of overall documentation.

Returns:
 This is also part of overall doc.
- - -
doc:
    "Part of overall documentation.\\n\\n This is also part of overall doc."
args:
    name: Documentation

## Section must be separated by blank line
Doc
Args:
    name: Part of Doc
- - -
doc: |
    Doc
    Args:
        name: Part of Doc

## Headers are case insensitive
args:
    name: Documentation

RETURNS: The result value.
- - -
args:
    name: Documentation
returns: The result value.

## "Arguments" header
Arguments:
    name: Documentation
- - -
args:
    name: Documentation

## "Parameters" header
PaRaMeTeRS:
    name: Documentation
- - -
args:
    name: Documentation

## "Return" header
Return:
    The result value.
- - -
returns: The result value.

## "Yields" header
Yields:
    The result value.
- - -
returns: The result value.

## Unrecognized sections
Doc

Args:
    name: Documentation

Raises:
    ValueError: If `name` is not accepted.
- - -
doc: |
    Doc

    Raises:
        ValueError: If `name` is not accepted.
args:
    name: Documentation

## Allow header formatting
*Args:*

    a: 1

**Args**:

    b: 2

_Args_:

    c: 3

__Args:__

    d: 4

_*Returns:*_

    Something
- - -
args:
    a: "1"
    b: "2"
    c: "3"
    d: "4"
returns:
    Something

## Support reStructuredText literal block marker (`::`)

Args::

    name: Documentation
- - -
args:
    name: Documentation
"""
        )

    def test_documentation(self):
        self.verify(
            """
## One line doc
Doc
- - -
doc:
    Doc

## Multiline doc
First line

Second paragraph
on multiple lines.
- - -
doc: |
    First line

    Second paragraph
    on multiple lines.

## Whitespace handling
First line


    def example():
        pass

The end
- - -
doc: |
    First line


        def example():
            pass

    The end

## Strip leading whitespace

    Doc
- - -
doc:
    Doc
"""
        )

    def test_arguments(self):
        self.verify(
            """
## Basics
Args:
    name: documentation
    NAME: https://example.com

    Name: Documentation
    _name: _documentation
- - -
args:
    name: documentation
    NAME: https://example.com
    Name: Documentation
    _name: _documentation

## Indentation handling
Args:
    empty:
    inline: doc
     off_by_one: parsed as own arg
      off_by_two: part of off_by_one
    own_line:
      own line
    multiline: Start.

      Doc continues.
    indentation1:
      Starts on own line.

            def example():
                pass

      The end
    indentation2: Starts on same line.
      Indentation is
        preserved.

    indentation3:
            Indentation
        is preserved.
- - -
args:
    empty: ""
    inline: doc
    off_by_one: |
        parsed as own arg
        off_by_two: part of off_by_one
    own_line: own line
    multiline: |
        Start.

        Doc continues.
    indentation1: |
        Starts on own line.

              def example():
                  pass

        The end
    indentation2: |
        Starts on same line.
        Indentation is
          preserved.
    indentation3:
        "    Indentation\\nis preserved."

## Multiple args sections
Args:
    name1: Documentation 1
    name2: Documentation 2

ARGS:
  name1: Overwrite 1
  name3: Documentation 3
- - -
args:
    name1: Overwrite 1
    name2: Documentation 2
    name3: Documentation 3

## Argument on the header line
Args:  name1: Documentation 1
       name2: Documentation 2
- - -
args:
    name1: Documentation 1
    name2: Documentation 2

## Invalid indentation
Args:
    name: Not found
  This sets indentation level
- - -
args:
    <no-name>: "  name: Not found\\nThis sets indentation level"

## Invalid content
Args:
    invalid content
    name: found
    part of name
- - -
args:
    <no-name>:
        invalid content
    name: |
        found
        part of name
"""
        )

    def test_normalize_name(self):
        self.verify(
            """
## Ignore spaces before and after colon
Args:
    before      : Before
    after:        After
    both     :    Both
- - -
args:
    before: Before
    after: After
    both: Both

## Remove types
Args:
    simple (str)      : Simple
    params (list[int]): Parameterized
    union (bool | str): Union
- - -
args:
    simple: Simple
    params: Parameterized
    union: Union

## Normalize varargs and kwargs
Args:
    *args: varargs
    **kws: kwargs
- - -
args:
    args: varargs
    kws: kwargs

## Normalize Robot args
Args:
    ${a  r  g}: argument
    @{args}   : varargs
    &{kws}    : kwargs
- - -
args:
    a  r  g: argument
    args: varargs
    kws: kwargs

## Ignore positional-only marker and keyword-only marker
Args:
    po: Positional-only argument
    /:  Positional-only marker
    normal: Normal argument
    *     : Keyword-only marker
    kwo   : Keyword-only argument
- - -
args:
    po: Positional-only argument
    normal: Normal argument
    kwo: Keyword-only argument

## Ignore code-style formatting
Args:
    `first`     : Markdown and reStructuredText style
    ``second``  : Robot and reStructuredText style
    `/`         : Positional-only marker is handled
    `*varargs`  : Varargs are normalized
    `  spaces  `: Spaces are stripped
- - -
args:
    first: Markdown and reStructuredText style
    second: Robot and reStructuredText style
    varargs: Varargs are normalized
    spaces: Spaces are stripped

## Empty name after normalization
Doc

Args:
    ${  }: Documentation
- - -
doc:
    Doc
args:
    <no-name>: Documentation
"""
        )

    def test_returns(self):
        self.verify(
            """
## Basics
Returns:
    The result value.
- - -
returns: The result value.

## Multiline
Returns:
    First line of return description
      that continues here.

        Indentation is
          preserved.

Args:
    name: Documentation
- - -
args:
    name: Documentation
returns: |
    First line of return description
      that continues here.

        Indentation is
          preserved.

## Inline
Returns: The result value.
- - -
returns: The result value.

## Inline and multiline
Returns: First line of return description
    that continues here.

        Indentation is
          preserved.
- - -
returns: |
    First line of return description
    that continues here.

        Indentation is
          preserved.

## Strip leading whitespace
Returns:

    The result value.
- - -
returns: The result value.
"""
        )


if __name__ == "__main__":
    unittest.main()
