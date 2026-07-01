.. _Documentation syntax:

Documentation formatting
========================

Robot Framework supports various documentation formats in different contexts:

- `Suite <Suite documentation_>`__ and `test <Test case documentation_>`__
  documentations use Robot Frameworks own custom format.
- Library and keyword documentation processed by Libdoc_ can be written using
  Robot Framework format, Markdown, reStructuredText, HTML and plain text.
- `Error messages`_ support plain text  and HTML.

The two main documentation formats are `Robot Framework's custom format`__ and
Markdown__, and they are documented thoroughly in this section. Before that,
this section explains how to handle whitespace in Robot Framework data when
writing documentation.

__ `Robot Framework format`_
__ `Markdown format`_

.. contents::
   :depth: 2
   :local:

Handling whitespace
-------------------

This section explains how newlines and spaces are handled in Robot Framework
data when writing documentation. These rules are the same regardless the
documentation format that is used.

Newlines
~~~~~~~~

When documenting and adding metadata to suites, tests and keywords, newlines can
be created by using the `\n` `escape sequence`_:

.. sourcecode:: robotframework

  *** Settings ***
  Documentation    First line.\n\nSecond paragraph. This time\nwith multiple lines.
  Metadata         Example list    - first item\n- second item\n- third

.. note:: As explained in the Paragraphs_ section below, the single newline in
          `Second paragraph, this time\nwith multiple lines.` does not actually
          affect how that paragraph is rendered. Newlines are needed when
          creating lists or other such constructs, though.

Adding newlines manually to a long documentation takes some effort and extra
characters also make the documentation harder to read. This can be avoided,
though, as newlines are inserted automatically
between `continued documentation and metadata lines`__. In practice this
means that the above example could be written also as follows:

.. sourcecode:: robotframework

  *** Settings ***
  Documentation
  ...    First line.
  ...
  ...    Second paragraph. This time
  ...    with multiple lines.
  Metadata
  ...    Example list
  ...    - first item
  ...    - second item
  ...    - third

No automatic newline is added if a line already ends with a literal newline
or if it ends with an `escaping backslash`__:

.. sourcecode:: robotframework

  *** Test Cases ***
  Ends with newline
      [Documentation]    Ends with a newline and\n
      ...                automatic newline is not added.

  Ends with backslash
      [Documentation]    Ends with a backslash and \
      ...                no newline is added.

__ `Dividing data to several rows`_
__ Escaping_

Spaces
~~~~~~

Unlike elsewhere in Robot Framework data, leading spaces and consecutive internal
spaces are preserved in documentation and metadata. This makes it possible, for example,
to split list items to multiple rows and have preformatted text with spaces:

.. sourcecode:: robotframework

  *** Test Cases ***
  Long list item
      [Documentation]
      ...    List:
      ...    - Short item.
      ...    - Second item is pretty long and it is split to
      ...      multiple rows. Leading spaces are preserved.
      ...    - Another short item.

  Preformatted text
      [Documentation]
      ...    Example with consecutive internal spaces:
      ...
      ...    | *** Test Cases ***
      ...    | Example
      ...    |     Keyword

.. note:: Preserving spaces in documentation and metadata is new in Robot Framework 6.1.
          With earlier versions spaces need to be escaped with a backslash.

Paragraphs
~~~~~~~~~~

Lines separated with a single newline are combined into a paragraph regardless whether
the newline is added manually or automatically. Multiple paragraphs can be separated
with an empty line (i.e. two newlines) and also tables, lists, and other
specially formatted blocks end paragraphs.

For example, this documentation:

.. sourcecode:: robotframework

  *** Settings ***
  Documentation
  ...    First paragraph has only one line.
  ...
  ...    Second paragraph, this time created
  ...    with multiple lines.

will be formatted in HTML like this:

.. raw:: html

  <div class="doc">
  <p>First paragraph has only one line.</p>
  <p>Second paragraph, this time created with multiple lines.</p>
  </div>

Robot Framework format
----------------------

Robot Framework has its own simple plain text documentation format. It can
be used when documenting suites and tests as well as when writing library
documentation. Its main benefit is that it does not require any additional
modules to be installed, but being a custom format means that it does not work
well with external documentation tools and that users new to Robot Framework
need to learn it.

.. _Robot inline styles:

Inline styles
~~~~~~~~~~~~~

The documentation syntax supports inline styles **bold**, *italics* and `code`.
Bold text can be created by having an asterisk before and after the
selected word or words, for example `*this is bold*`. The italics
style works similarly, but the special character to use is an
underscore, for example, `_italics_`. It is also possible to have
bold italics with the syntax `_*bold italics*_`.

The code style is created using double backticks like :codesc:`\`\`code\`\``.
The result is monospaced text with light gray background.

Asterisks, underscores or double backticks alone, or in the middle of a word,
do not start formatting, but punctuation characters before or after them
are allowed. When multiple lines form a paragraph__, all inline styles can
span over multiple lines.

__ paragraphs_

.. raw:: html

   <table class="tabular docutils">
     <caption>Inline style examples</caption>
     <tr>
       <th>Source</th>
       <th>Formatted</th>
     </tr>
     <tr>
       <td>*bold*</td>
       <td><b>bold</b></td>
     </tr>
     <tr>
       <td>_italics_</td>
       <td><i>italics</i></td>
     </tr>
     <tr>
       <td>_*bold italics*_</td>
       <td><i><b>bold italics</b></i></td>
     </tr>
     <tr>
       <td>``code``</td>
       <td><code>code</code></td>
     </tr>
     <tr>
       <td>*bold*, then _italics_ and finally ``some code``</td>
       <td><b>bold</b>, then <i>italics</i> and finally <code>some code</code></td>
     </tr>
     <tr>
       <td>This is *bold\n<br>on multiple\n<br>lines*.</td>
       <td>This is <b>bold</b><br><b>on multiple</b><br><b>lines</b>.</td>
     </tr>
   </table>

URL detection
~~~~~~~~~~~~~

All strings that look like URLs are automatically converted into
clickable links. Additionally, URLs that end with extension
:file:`.jpg`, :file:`.jpeg`, :file:`.png`, :file:`.gif`, :file:`.bmp` or
:file:`.svg` (case-insensitive) will automatically create images. For
example, URLs like `http://example.com` are turned into links, and
`http:///host/image.jpg` and `file:///path/chart.png`
into images.

The automatic conversion of URLs to links is applied to all the data
in logs and reports, but creating images is done only for test suite,
test case and keyword documentation, and for test suite metadata.

Custom links and images
~~~~~~~~~~~~~~~~~~~~~~~

It is possible to create custom links
and embed images using special syntax `[link|content]`. This creates
a link or image depending are `link` and `content` images.
They are considered images if they have the same image extensions that are
special with `URLs <URL detection_>`__ or start with `data:image/`. The surrounding square
brackets and the pipe character between the parts are mandatory in all cases.

Link with text content
''''''''''''''''''''''

If neither `link` nor `content` is an image, the end result is
a normal link where `link` is the link target and `content`
the visible text::

    [file.html|this file] -> <a href="file.html">this file</a>
    [http://host|that host] -> <a href="http://host">that host</a>

Link with image content
'''''''''''''''''''''''

If `content` is an image, you get a link where the link content is an
image. Link target is created by `link` and it can be either text or image::

    [robot.html|robot.png] -> <a href="robot.html"><img src="robot.png"></a>
    [robot.html|data:image/png;base64,oooxxx=] -> <a href="robot.html"><img src="data:image/png;base64,oooxxx="></a>
    [image.jpg|thumb.jpg] -> <a href="image.jpg"><img src="thumb.jpg"></a>

Image with title text
'''''''''''''''''''''

If `link` is an image but `content` is not, the syntax creates an
image where the `content` is the title text shown when mouse is over
the image::

    [robot.jpeg|Robot rocks!] -> <img src="robot.jpeg" title="Robot rocks!">
    [data:image/png;base64,oooxxx=|Robot rocks!] -> <img src="data:image/png;base64,oooxxx=" title="Robot rocks!">

Section headers
~~~~~~~~~~~~~~~

If documentation gets longer, it is often a good idea to split it into sections.
It is possible to separate sections with headers using syntax `= My Header =`,
where the number of equal signs denotes the header level::

    = First section =

    == Subsection ==

    Some text.

    == Second subsection ==

    More text.

    = Second section =

    You probably got the idea.

Notice that only three header levels are supported and that spaces between
equal signs and the header text are mandatory.

Tables
~~~~~~

Tables are created using pipe characters with spaces around them
as column separators and newlines as row separators. Header
cells can be created by surrounding the cell content with equal signs
and optional spaces like `= Header =` or `=Header=`. Tables
cells can also contain links and formatting such as bold and italics::

   | =A= |  =B=  | = C =  |
   | _1_ | Hello | world! |
   | _2_ | Hi    |

The created table always has a thin border and normal text is left-aligned.
Text in header cells is bold and centered. Empty cells are automatically
added to make rows equally long. For example, the above example would be
formatted like this in HTML:

.. raw:: html

  <div class="doc">
    <table>
      <tr><th>A</th><th>B</th><th>C</th></tr>
      <tr><td><i>1</i></td><td>Hello</td><td>world</td></tr>
      <tr><td><i>2</i></td><td>Hi</td><td></td></tr>
    </table>
  </div>

Lists
~~~~~

Lists are created by starting a line with a hyphen and space (:codesc:`-\ `).
List items can be split into multiple lines by indenting continuing lines with
one or more spaces. A line that does not start with :codesc:`-\ ` and is not
indented ends the list::

  Example:
  - a list item
  - second list item is split
    to multiple lines

  This is outside the list.

The above documentation is formatted like this in HTML:

.. raw:: html

  <div class="doc">
  <p>Example:</p>
  <ul>
    <li>a list item</li>
    <li>second list item is split to multiple lines</li>
  </ul>
  <p>This is outside the list.</p>
  </div>

Preformatted text
~~~~~~~~~~~~~~~~~

It is possible to embed blocks of preformatted text in the documentation.
Preformatted block is created by starting lines with :codesc:`|\ `, one
space being mandatory after the pipe character except on otherwise empty lines.
The starting :codesc:`|\ ` sequence will be removed from the resulting HTML,
but all other whitespace is preserved.

In the following documentation, the two middle lines form a preformatted
block when converted to HTML::

  Doc before block:
  | inside block
  |     some    additional whitespace
  After block.

The above documentation is formatted like this:

.. raw:: html

  <div class="doc">
  <p>Doc before block:</p>
  <pre>inside block
      some    additional whitespace</pre>
  <p>After block.</p>
  </div>

Horizontal ruler
~~~~~~~~~~~~~~~~

Horizontal rulers (the `<hr>` tag) make it possible to separate larger
sections from each others, and they can be created by having three or more
hyphens alone on a line::

   Some text here.

   ---

   More text...

The above documentation is formatted like this:

.. raw:: html

  <div class="doc">
  <p>Some text here.</p>
  <hr>
  <p>More text...</p>
  </div>

Markdown format
---------------

Markdown_ is a lightweight plain text markup syntax that is very widely used
for documentation, README files, and technical content across the software
development industry.

Starting from Robot Framework 7.5, Markdown is supported by Libdoc_ and can
be used for documenting libraries and user keywords. The plan is to add support
for using Markdown in suite and test documentation in the future as well.

Markdown flavors
~~~~~~~~~~~~~~~~

The biggest problem with Markdown is that different Markdown implementations
are not fully compatible with each others. The original `Markdown implementation`__
had a somewhat informal specification and also lacked commonly needed features
such as tables. The `Markdown ecosystem diverged`__ when new implementations
handled ambiguous cases differently and implemented missing features in different
ways.

The CommonMark_ specification tries to unify Markdown syntax, but especially
older tools still follow the original specification. The good news is that
basic features work the same way across implementations.

Robot Framework uses the Python-Markdown_ module as its underlying Markdown
engine. It follows the original implementation closely and is explicitly *not*
CommonMark compliant. It supports basic Markdown features out-of-the-box, but
the following extensions are enabled and provide some more functionality:

- `Admonition <https://python-markdown.github.io/extensions/admonition/>`__
  for adding notes, tips and warnings.
- `Code Hilite <https://python-markdown.github.io/extensions/code_hilite/>`__
  for syntax highlighting.
- `Fenced Code Blocks <https://python-markdown.github.io/extensions/fenced_code_blocks/>`__
  for common code block syntax.
- `Sane Lists <https://python-markdown.github.io/extensions/sane_lists/>`__
  to make lists syntax less surprising.
- `Table of Contents <https://python-markdown.github.io/extensions/toc/>`__
  for automatically generating table of contents.
- `Tables <https://python-markdown.github.io/extensions/tables/>`__
  for table support.
- A `custom plugin <https://github.com/robotframework/robotframework/blob/master/src/robot/utils/markdown.py>`__
  for linkifying URLs.

In this documentation we cover the most important Markdown features and note when
syntax is not common across tools. For details about the supported syntax it is
best to refer to the `original Markdown specification`__ that Python-Markdown
closely follows. The specification covers also various features not mentioned
here at all.

__ https://daringfireball.net/projects/markdown
__ https://en.wikipedia.org/wiki/Markdown#Rise_and_divergence
__ https://daringfireball.net/projects/markdown/syntax

Installation
~~~~~~~~~~~~

Python-Markdown_ is an optional dependency and users need to install__ it
themselves. That is typically done by running::

    pip install markdown

If syntax highlighting is needed, also Pygments_ needs to be installed::

    pip install pygments

__ https://python-markdown.github.io/install/

Inline styles
~~~~~~~~~~~~~

Markdown supports inline styles **bold**, *italics* and `code`. Bold text can
be created by surrounding text with two asterisks or underscores like
`**this is bold**` or `__this is bold__`. The italics style works similarly,
but there must be only a single asterisk or underscore like `*italics*` or
`_italics_`. Using three asterisks or underscores produces bold italics like
`***bold italics***` or `___bold italics___`.

The code style is created using backticks like :codesc:`\`code\``.
Asterisks or underscores do not have a special meaning inside backticks,
so something like :codesc:`\`__str__\`` is formatted as code with `__str__`
and not as bold code with only `str`.

Example:

.. sourcecode:: markdown

    Here we have some **bold text**, some *italics* and finally some `code`.

Linking
~~~~~~~

Inline links
''''''''''''

The most common way to create links in Markdown is using inline links like
`[an example](http://example.com)`. This link syntax supports also optional
title text like `[an example](http://example.com "Optional title")`.

Example:

.. sourcecode:: markdown

    [Robot Framework](http://robotframework.org) development is supported by
    [Robot Framework Foundation](http://robotframework.org/foundation "Join us!").

Reference links
'''''''''''''''

Markdown also supports reference links like `[link text][reference]`. This
is especially convenient if the link target is long or if it is used multiple
times. Using this style requires the reference to be created separately using
syntax `[reference]: http://example.com "Optional title"` somewhere in the
document.

Example:

.. sourcecode:: markdown

    [Robot Framework][robot] development is supported by
    [Robot Framework Foundation][foundation].

    [robot]: http://robotframework.org
    [foundation]: http://robotframework.org/foundation "Join us!"

If the reference name matches the link text, it is possible to shorten
the syntax to just `[reference]`. Reference matching is case-insensitive
in general and in with Robot Framework also spaces and underscores are ignored.

Example:

.. sourcecode:: markdown

    [Robot Framework] development is supported by [Robot Framework Foundation].

    [Robot Framework]: http://robotframework.org
    [Robot Framework Foundation]: http://robotframework.org/foundation "Join us!"

Depending on the context, there may also be automatic reference
targets available. For example, Libdoc_ makes keywords, section headers
and argument types available as link targets automatically.

Autolinks
'''''''''

URLs and email addresses inside `<` and `>` are automatically made clickable
links and the surrounding angle brackets are removed:

.. sourcecode:: markdown

    Our website is at <http://example.com>. You can reach us via <info@example.com>.

URLs are recognized also without special formatting:

.. sourcecode:: markdown

    Robot Framework website is at http://robotframework.org.

.. note:: Automatic URL detection is not a standard Markdown feature, but various
          Markdown implementations support it for convenience.

Tables
~~~~~~

Tables are created by separating columns with pipes and using hyphen for
separating headers from rest of the table. The whole table can be surrounded
with pipes as well, but that is not required.

Example:

.. sourcecode:: markdown

    Header 1 | Header 2 | Header 3
    -------- | -------- | --------
    First    | Second   | Third
    a        | b        | c

Headers are center aligned and other cells left aligned by default. That can
be controlled by starting or ending the hyphen line with a colon like `:---` (left),
`---:` (right) and `:--:` (center), but this then affects the whole column.

Example:

.. sourcecode:: markdown

    | Left   |  Center  |  Right |
    | :----- | :------: | -----: |
    | First  |  Second  |  Third |
    | a      |     b    |      c |

Tables support inline styles and links, but not block level content like lists.

.. note:: Tables are supported via Python-Markdown's tables__ plugin.

.. note:: Tables are not a standard Markdown feature and neither the original
          Markdown implementation nor CommonMark_ supports them. The above
          syntax is somewhat widely used, though.

__ https://python-markdown.github.io/extensions/tables/

Lists
~~~~~

Unordered lists
'''''''''''''''

Unordered lists can be created using `*`, `+` or `-` as the list marker followed
with one or more spaces:

.. sourcecode:: markdown

    - First item.
    - Second item.

Ordered lists
'''''''''''''

Ordered lists are created with a number followed by a period and one or more
spaces:

.. sourcecode:: markdown

    1. First item.
    2. Second item.

Splitting lines
'''''''''''''''

If a list item is long, it can be split to multiple lines. Indenting lines
is not necessary, but it makes the syntax easier to read.

Example:

.. sourcecode:: markdown

    - This list item is pretty long. It is thus
      split to multiple lines.
    - The second item is short.

Nested content
''''''''''''''

Nested lists are supported, but they *must be indented by four spaces*.
Empty rows can be added between lists, but they are not mandatory.

Example:

.. sourcecode:: markdown

    1. First item.
        - Nested unordered item.
        - Another nested item.
    2. Second item.
        1. Nested ordered item.
        2. Another nested item.

If a list item has multiple paragraphs or other content such as tables, also they
*must be indented with four spaces*. The initial content can be aligned to
the same level to avoid inconsistent alignment.

Example:

.. sourcecode:: markdown

    -   First item has multiple paragraphs. This is the first one.
        Notice the optional four space alignment.

        This is the second paragraph. Here the four space
        alignment is mandatory.

    -   Second item has a table. Empty rows above and below this
        paragraph are optional, but enhance readability.

        H1 | H2 | H3
        -- | -- | --
        a  | b  | c
        1  | 2  | 3

.. note:: The required list item indentation varies between Markdown implementations
          and some implementations also require empty lines before lists. Test your
          markup with different tools if you have strict interoperability needs.

Section headers
~~~~~~~~~~~~~~~

The most common syntax for section headers is `# Header` where the number
of hash characters specifies the header level. This syntax supports up to
six header levels.

Example:

.. sourcecode:: markdown

    # Top level heading

    ## Second level

    Some content.

    ## Second level again

    ### Third level

    The end.

Alternatively headers can be underlined with `=` (level 1) and `-` (level 2).
This syntax supports only two header levels.

Example:

.. sourcecode:: markdown

    Top level heading
    =================

    Second level
    ------------

    Some content.

    Second level again
    ------------------

    The end.

Table of contents
~~~~~~~~~~~~~~~~~

Table of contents can be inserted by using a `%TOC%` marker. It is generated
automatically based on the used `section headers`_ so that the two highest
level headers are included.

Example:

.. sourcecode:: markdown

    %TOC%

    # Top level

    This section is included in TOC.

    ## Second level

    Also this section is included in TOC.

    ### Third level

    This section is not included in TOC.

    # Top level again

    This section is included in TOC.

Libdoc_ supports the `%TOC%` marker also when `creating table of contents`_
with the Robot Framework custom format. In that format only the top level
headers are included in the generated table of contents.

.. note:: Generating table of contents is not a standard Markdown feature and
          even the marker used by Robot Framework is different to what
          Python-Markdown's toc__ plugin uses by default.

__ https://python-markdown.github.io/extensions/toc/

Code blocks
~~~~~~~~~~~

Fenced code blocks
''''''''''''''''''

Fenced code blocks are the most common way to format code in Markdown. They
start with an opening fence of three or more backtick (:codesc:`\`\`\``) or
tilde (`~~~`) characters and are closed with a matching fence. The opening
fence can also contain the language name and possible other information
for the underlying Markdown engine.

Example:

.. sourcecode:: markdown

    Here's some Python code:

    ```python
    def hello(name):
        print(f"Hello, {name}!")

    hello("Robot")
    ```

Syntax highlighting
'''''''''''''''''''

If a language is specified and Pygments_ syntax highlighter is installed,
the code will be syntax highlighted. Pygments supports also Robot Framework
out-of-the-box which makes creating examples easy.

Example:

.. sourcecode:: python

    def hello(name):
        """Keyword to greet the thing specified with `name`.

        ```robotframework
        *** Test Cases ***
        Example
            Hello    Robot
        ```
        """
        print(f"Hello, {name}!")

Indented code blocks
''''''''''''''''''''

Code blocks can also be created by using four space indentation. The used
CodeHilite__ plugin supports highlighting also in that case if the code
starts with shebang like `#!python` or with three colons followed by
the language name like `:::robotframework`.

Example:

.. sourcecode:: markdown

    Here's some Python code:

        #!python
        def hello(name):
            print(f"Hello, {name}!")

        hello("Robot")

__ https://python-markdown.github.io/extensions/code_hilite/#syntax

Admonitions
~~~~~~~~~~~

Admonitions make it easy to create notes, tips and warnings that stand out
from the normal text. The syntax is as follows:

.. sourcecode:: markdown

    !!! type "Optional title"
        Admonition text. Can contain multiple paragraphs and normal formatting.

Robot Framework supports certain admonition types so that they have a different
styles:

- note (blueish)
- tip (greenish)
- warning (yellowish)
- danger (redish)

If a type is not recognized, it is treated the same way as a note. If the
optional title is omitted, the capitalized type name is used instead.

Example:

.. sourcecode:: markdown

    Markdown is a great documentation syntax!

    !!! note
        Markdown support is new in *Robot Framework 7.5*.

    !!! warning "Interoperability risk"
        Differences between Markdown flavors can cause problems.

.. note:: Admonitions are implemented using Python-Markdown's
          `Admonition <https://python-markdown.github.io/extensions/admonition/>`__
          extension.

.. note:: Admonitions are not a standard Markdown feature. Some other tools support
          them as well, but they typically use different syntax. Use other formatting
          for notes, tips, etc. if interoperability is important.
