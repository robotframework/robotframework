Robot Framework User Guide
==========================

Introduction
------------

Robot Framework User Guide was created with a text editor, using
`reStructuredText (reST)`_, which is the markup syntax and parser
component of Docutils_. In reST, simple markup is used to indicate
special parts of text, such as section headings, bullet lists, and
emphasis. Some general formatting principles of reST that are followed
in Robot Framework User Guide are presented here.

Generating Robot Framework User Guide in the HTML format
--------------------------------------------------------

The precondition for generating Robot Framework User Guide is
installing Docutils_ and Pygments_::

    pip install docutils pygments

Robot Framework User Guide can then be generated with `<ug2html.py>`__ script.
Run it without arguments to get the usage::

    python ug2html.py

Source files are under `<src>`__ directory. `<src/RobotFrameworkUserGuide.rst>`__
includes other section specific files.

Section style principles of reST
--------------------------------

Titles are underlined (or both over- and underlined) with a printing
non-alphanumeric 7-bit ASCII character. The options recommended by
reST are "= - ` : ' " ~ ^ _ * + # < >". The underline/overline must be
at least as long as the title text.

Rather than using a fixed number and order of section title styles,
the order enforced is the order as encountered. The first style
encountered becomes the outermost title, the second style is a
subtitle, the third is a subsubtitle, and so on.

Formatting used in Robot Framework User Guide
---------------------------------------------

The section title styles used in Robot Framework User Guide are the
following, in this order::

   ==============
     Main title
   ==============

   -------------
      Version
   -------------

   ~~~~~~~~~~~~~~~~
     Chapter title
   ~~~~~~~~~~~~~~~~

   Section title
   =============

   Subsection title
   ----------------

   Subsubsection title
   ~~~~~~~~~~~~~~~~~~~

   Paragraph title
   '''''''''''''''

   Section title
   `````````````

Roles used in Robot Framework User Guide
----------------------------------------

For the formatting roles, which are used in Robot Framework User Guide
to make it easier for the reader to distinguish certain parts of the
text, see the file `<src/roles.rst>`__.

Using source code directive with files
--------------------------------------

The source code directive can be used also to read the source code from a file.
In this case, the path to the file must be relative to the root directory of
the user guide, for example::

   ..sourcecode:: python

   ExtendingRobotFramework/check_test_times.py

References
----------

For more information on Docutils reST, see `Quick reStructuredText`_
and `reStructuredText Markup Specification`_.


.. _Pygments: http://pygments.org/download/
.. _Docutils: http://docutils.sourceforge.net/
.. _reStructuredText (reST): http://docutils.sourceforge.net/rst.html
.. _Quick reStructuredText: http://docutils.sourceforge.net/docs/user/rst/quickref.html
.. _reStructuredText Markup Specification: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html
