"""Module test library."""

from robot.api import deco

__version__ = "0.1-alpha"


def keyword(a1="d", *a2):
    """A keyword.

    See `get hello` for details.
    """
    pass


def get_hello():
    """Get hello.

    See `importing` for explanation of nothing
    and `introduction` for no more information.
    """
    return "foo"


def non_string_defaults(a=1, b=True, c=(1, 2, None)):
    pass


def non_ascii_string_defaults(arg="hyvä"):
    pass


def non_ascii_bytes_defaults(arg=b"hyv\xe4"):
    pass


def multiline_doc_with_split_short_doc():
    """This is short doc.
    It can span multiple
    physical
    lines and contain *formatting*.

    This is body. It can naturally also
    contain multiple lines.

    And paragraphs.
    """


def non_ascii_doc():
    """Hyvää yötä.

    Спасибо!
    """


def non_ascii_doc_with_escapes():
    """Hyv\xe4\xe4 y\xf6t\xe4."""


@deco.keyword("Set Name Using Robot Name Attribute")
def name_set_in_method_signature(a, b, *args, **kwargs):
    """
    This makes sure that @deco.keyword decorated kws don't lose their signatures
    """
    pass


@deco.keyword("Takes ${embedded} ${args}")
def takes_embedded_args(a=1, b=2):
    """A keyword which uses embedded args."""
    pass


@deco.keyword("Takes ${embedded} and normal args")
def takes_embedded_and_normal(embedded, mandatory, optional=None):
    """A keyword which uses embedded and normal args."""
    pass


@deco.keyword("Takes ${embedded} and positional-only args")
def takes_embedded_and_pos_only(embedded, mandatory, /, optional=None):
    """A keyword which uses embedded, positional-only and normal args."""
    pass


@deco.keyword(tags=["1", 1, "one", "yksi"])
def keyword_with_tags_1():
    pass


@deco.keyword("Keyword with tags 2", ("2", 2, "two", "kaksi"))
def setting_both_name_and_tags_by_decorator():
    pass


def keyword_with_tags_3():
    """Set tags in documentation.

    Tags: tag1, tag2
    """


def robot_espacers(arg=" robot  escapers\n\t\r  "):
    pass
