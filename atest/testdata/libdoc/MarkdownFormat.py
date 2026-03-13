"""Library documentation in *Markdown* format.

%TOC%

# Basic formatting

Basic Markdown formatting such as **bold**, *italics* and `code` works as expected.

# Linking

## Link syntax

Normal Markdown [inline](http://example.com) and [reference] links are supported.

[reference]: http://example.com "An example"

## Automatic reference targets

Three kind of reference link targets are generated automatically to make internal
linking easy:

- Keywords like [References] and [admonitions].
- Headers in the library introduction like [linking] and [Basics].
- Predefined targets like [Introduction] and [keywords].

Link targets are case and space insensitive. The concept and automatically
available targets are the same as when using the Robot format, but the difference
is that only the Markdown link syntax works. Using backticks like `introduction`
does create a link, not even when escaped like \\`introduction\\`.

# Advanced syntax

Keywords demonstrate more advanced syntax provided partly by built-in
Python Markdown plugins that are separately activated. This includes [lists],
[tables], [syntax highlighting] and [admonitions].

# Table of contents

## Basics

Table of contents is generated automatically based on the headers using Python
Markdown's `toc` plugin. The plugin uses the `[TOC]` marker by default, but we
use `%TOC%` that is used also with the Robot format.

    # This is not a header!

```python
# This is not a header either!
```

## Differences to Robot format

A difference compared to the Robot format is that the generated TOC does not get
links to the Importing and Keywords sections automatically. This can be changed
later if it is considered a problem. Instead of adding them to the TOC also with
Markdown, we could enhance HTML outputs so that both sections are always easily
accessible, though. Keywords already are, so this would require only making the
Importing section somehow directly accessible, and then we wouldn't need these
sections in the TOC with either format.

Another small difference is that with Markdown TOC works everywhere, but with
the Robot format TOC works only in the Introduction. Enhancing the Robot format
so that it supports TOC everywhere wouldn't be too hard, though. See the [TOC]
keyword for an example.
"""

ROBOT_LIBRARY_DOC_FORMAT = "MARKDOWN"


def references():
    """
    We can link to predefined targets like [introduction], to intro headers
    like [linking] and to keywords like [Admonitions].

    Custom references defined elsewhere like [reference] do not work.
    """


def admonitions():
    """
    !!! note
        Admonitions are provided by the `admonition` plugin.

        We need to make sure to add custom styles to make them render nicely.

    !!! warning "Interoperability risk!"
        Admonitions are not standard Markdown. Don't use them if you want good
        interoperability with other Markdown tools.
    """


def syntax_highlighting():
    """
    The first examples use fenced code blocks provided by the `fenced_code`
    plugin. Actual syntax highlighting is provided by `codehilite`.

    ```robotframework
    *** Test Cases ***
    Example
        Keyword    arg
    ```
    ~~~python
    def keyword(arg):
        print(arg)
        # This is comment in code, not a Markdown header!
    ~~~

    Python Markdown also supports indented code blocks:

        #!python
        print("Fenced blocks are more commonly used.")
    """


def lists():
    """
    # Unordered lists

    - First unordered item.
    - Second item.

    # Ordered lists

    1. First ordered item.
    2. Second item.

    # Nested lists

    1. First item in an ordered list.
        - Nested unordered item.
        - Another nested item.
    2. Second item.
        1. Nested ordered item.
        2. Another nested item.

    - First item in an unordered list.
        - Nested unordered item.
        - Another nested item.
    - Second item.
        1. Nested ordered item.
        2. Another nested item.
    """


def tables():
    """
    Header 1 | Header 2 | Header 3
    -------- | -------- | --------
    item 1.1 | item 2.1 | item 3.1
    item 1.2 | item 2.2 | item 3.2

    | Left | Center | Right |
    | :--- | :----: | ----: |
    | 1234567890 | 1234567890 | 1234567890 |
    """


def toc():
    """Table of contents.

    %TOC%

    ## Where it works?

    Both with [keywords] and in [introduction].

    ## Where to learn more?

    See the [Table of contents] section.
    """
