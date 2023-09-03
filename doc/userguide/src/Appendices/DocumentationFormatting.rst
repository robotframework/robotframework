.. _Documentation syntax:

Documentation formatting
========================

It is possible to use simple HTML formatting with `test suite`__,
`test case`__ and `user keyword`__ documentation and `free suite
metadata`_ in the test data, as well as when `documenting test
libraries`__.  The formatting is similar to the style used in most
wikis, and it is designed to be understandable both as plain text and
after the HTML transformation.

__ `suite documentation`_
__ `test case documentation`_
__ `user keyword documentation`_
__ `Documenting libraries`_

.. contents::
   :depth: 2
   :local:

Handling whitespace in test data
--------------------------------

Newlines
~~~~~~~~

When documenting test suites, test cases and user keywords or adding metadata
to test suites, newlines can be added manually using `\n` `escape sequence`_.

.. sourcecode:: robotframework

  *** Settings ***
  Documentation    First line.\n\nSecond paragraph. This time\nwith multiple lines.
  Metadata         Example list    - first item\n- second item\n- third

.. note:: As explained in the Paragraphs_ section below, the single newline in
          `Second paragraph, this time\nwith multiple lines.` does not actually
          affect how that paragraph is rendered. Newlines are needed when
          creating lists_ or other such constructs, though.

Adding newlines manually to a long documentation takes some effort and extra
characters also make the documentation harder to read. This can be avoided,
though, as newlines are inserted automatically
between `continued documentation and metadata lines`__. In practice this
means that the above example could be written also as follows.

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
to split `list items`__ to multiple rows and have `preformatted text`_ with spaces:

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

__ lists_

.. note:: Preserving spaces in documentation and metadata is new in Robot Framework 6.1.
          With earlier versions spaces need to be escaped with a backslash.

Paragraphs
----------

All regular text in the formatted HTML
documentation is represented as paragraphs. In practice, lines separated
by a single newline will be combined in a paragraph regardless whether the
newline is added manually or automatically. Multiple paragraphs can be separated
with an empty line (i.e. two newlines) and also tables, lists, and other
specially formatted blocks discussed in subsequent sections end a paragraph.

For example, the following test suite or resource file documentation:

.. sourcecode:: robotframework

  *** Settings ***
  Documentation
  ...    First paragraph has only one line.
  ...
  ...    Second paragraph, this time created
  ...    with multiple lines.

will be formatted in HTML as:

.. raw:: html

  <div class="doc">
  <p>First paragraph has only one line.</p>
  <p>Second paragraph, this time created with multiple lines.</p>
  </div>

Inline styles
-------------

The documentation syntax supports inline styles **bold**, *italic* and `code`.
Bold text can be created by having an asterisk before and after the
selected word or words, for example `*this is bold*`. Italic
style works similarly, but the special character to use is an
underscore, for example, `_italic_`. It is also possible to have
bold italic with the syntax `_*bold italic*_`.

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
       <th>Unformatted</th>
       <th>Formatted</th>
     </tr>
     <tr>
       <td>*bold*</td>
       <td><b>bold</b></td>
     </tr>
     <tr>
       <td>_italic_</td>
       <td><i>italic</i></td>
     </tr>
     <tr>
       <td>_*bold italic*_</td>
       <td><i><b>bold italic</b></i></td>
     </tr>
     <tr>
       <td>``code``</td>
       <td><code>code</code></td>
     </tr>
     <tr>
       <td>*bold*, then _italic_ and finally ``some code``</td>
       <td><b>bold</b>, then <i>italic</i> and finally <code>some code</code></td>
     </tr>
     <tr>
       <td>This is *bold\n<br>on multiple\n<br>lines*.</td>
       <td>This is <b>bold</b><br><b>on multiple</b><br><b>lines</b>.</td>
     </tr>
   </table>

URLs
----

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

.. note:: :file:`.svg` image support is new in Robot Framework 3.2.

Custom links and images
-----------------------

It is possible to create custom links
and embed images using special syntax `[link|content]`. This creates
a link or image depending are `link` and `content` images.
They are considered images if they have the same image extensions that are
special with URLs_ or start with `data:image/`. The surrounding square
brackets and the pipe character between the parts are mandatory in all cases.

.. note:: Support for the `data:image/` prefix is new in Robot Framework 3.2.

Link with text content
~~~~~~~~~~~~~~~~~~~~~~

If neither `link` nor `content` is an image, the end result is
a normal link where `link` is the link target and `content`
the visible text::

    [file.html|this file] -> <a href="file.html">this file</a>
    [http://host|that host] -> <a href="http://host">that host</a>

Link with image content
~~~~~~~~~~~~~~~~~~~~~~~

If `content` is an image, you get a link where the link content is an
image. Link target is created by `link` and it can be either text or image::

    [robot.html|robot.png] -> <a href="robot.html"><img src="robot.png"></a>
    [robot.html|data:image/png;base64,oooxxx=] -> <a href="robot.html"><img src="data:image/png;base64,oooxxx="></a>
    [image.jpg|thumb.jpg] -> <a href="image.jpg"><img src="thumb.jpg"></a>

Image with title text
~~~~~~~~~~~~~~~~~~~~~

If `link` is an image but `content` is not, the syntax creates an
image where the `content` is the title text shown when mouse is over
the image::

    [robot.jpeg|Robot rocks!] -> <img src="robot.jpeg" title="Robot rocks!">
    [data:image/png;base64,oooxxx=|Robot rocks!] -> <img src="data:image/png;base64,oooxxx=" title="Robot rocks!">

Section titles
--------------

If documentation gets longer, it is often a good idea to split it into
sections. It is possible to separate
sections with titles using syntax `= My Title =`, where the number of
equal signs denotes the level of the title::

    = First section =

    == Subsection ==

    Some text.

    == Second subsection ==

    More text.

    = Second section =

    You probably got the idea.

Notice that only three title levels are supported and that spaces between
equal signs and the title text are mandatory.

Tables
------

Tables are created using pipe characters with spaces around them
as column separators and newlines as row separators. Header
cells can be created by surrounding the cell content with equal signs
and optional spaces like `= Header =` or `=Header=`. Tables
cells can also contain links and formatting such as bold and italic::

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
-----

Lists are created by starting a line with a hyphen and space ('- '). List items
can be split into multiple lines by indenting continuing lines with one or more
spaces. A line that does not start with '- ' and is not indented ends the list::

  Example:
  - a list item
  - second list item
    is continued

  This is outside the list.

The above documentation is formatted like this in HTML:

.. raw:: html

  <div class="doc">
  <p>Example:</p>
  <ul>
    <li>a list item</li>
    <li>second list item is continued</li>
  </ul>
  <p>This is outside the list.</p>
  </div>

Preformatted text
-----------------

It is possible to embed blocks of
preformatted text in the documentation. Preformatted block is created by
starting lines with '| ', one space being mandatory after the pipe character
except on otherwise empty lines. The starting '| ' sequence will be removed
from the resulting HTML, but all other whitespace is preserved.

In the following documentation, the two middle lines form a preformatted
block when converted to HTML::

  Doc before block:
  | inside block
  |    some   additional whitespace
  After block.

The above documentation is formatted like this:

.. raw:: html

  <div class="doc">
  <p>Doc before block:</p>
  <pre>inside block
    some   additional whitespace</pre>
  <p>After block.</p>
  </div>

Horizontal ruler
----------------

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
