from os.path import abspath, join

__all__ = [  # noqa: PLE0604
    "join_with_execdir",
    "abspath",
    "attr_is_not_kw",
    "_not_kw_even_if_listed_in_all",
    "extra stuff",  # noqa: F822
    None,
]


def join_with_execdir(arg):
    return join(abspath("."), arg)


def not_in_all():
    pass


attr_is_not_kw = "Listed in __all__ but not a function"


def _not_kw_even_if_listed_in_all():
    print("Listed in __all__ but starts with an underscore")
