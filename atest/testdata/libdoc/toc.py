"""
== Table of contents ==
%TOC%

= First level =

First level headers are included in TOC.

= First level again =

Yes, also this header is included.

== Second level ==

Also second level headers are included starting from RF 7.5.

=== Third level ===

Third level headers aren't included.

   == Second level again ==

This is included. Header indentation doesn't matter.

= First level once more =
== Second level once more ==

These are included.

= Just = text
here =

%TOC% isn't replaced when not alone.

Not even here:
%TOC%
"""


def keyword():
    """Some documentation.

    This is pretty long to make it easier to test how TOC works.

    This is pretty long to make it easier to test how TOC works.

    This is pretty long to make it easier to test how TOC works.

    This is pretty long to make it easier to test how TOC works.

    This is pretty long to make it easier to test how TOC works.

    This is pretty long to make it easier to test how TOC works.

    This is pretty long to make it easier to test how TOC works.

    This is pretty long to make it easier to test how TOC works.

    We also have links to `First level`, `Second level` and `Third level`.
    """
    pass
