"""Library for ``libdoc.html`` testing.

*URL:*    http://robotframework.org

_Image:_  https://github.com/robotframework/visual-identity/raw/master/logo/robot-framework.svg

_*Cross linking*_: `Links`, `One Paragraph`, `HR`, `hr`.
`section`, `Nön-ÄSCÏÏ`, `Special ½!"#¤%&/()=?<|>+-_.!~*'() chars`

----------------------------

= Section =
== Subsection with Ääkköset ==

| *My* | *Table* |
| 1    | 2       |
| foo  |
regular line
| block formatted
|    content\t\tand whitespaces
"""

from datetime import date
from enum import Enum
from typing import TypedDict, Union

from robot.api.deco import keyword, not_keyword


not_keyword(TypedDict)


@not_keyword
def parse_date(value: str):
    """Date in format ``dd.mm.yyyy``."""
    d, m, y = [int(v) for v in value.split('.')]
    return date(y, m, d)


class Direction(Enum):
    """Move direction."""
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Point(TypedDict):
    """Pointless point."""
    x: int
    y: int


class date2(date):
    pass


ROBOT_LIBRARY_CONVERTERS = {date: parse_date}


def type_hints(a: int, b: Direction, c: Point, d: date, e: bool = True, f: Union[int, date] = None):
    """We use `integer`, `date`, `Direction`, and many other types."""
    pass


def type_aliases(a: date, b: date2):
    pass


def int10(i: int):
    pass


int1 = int2 = int3 = int4 = int5 = int6 = int7 = int8 = int9 = int10


def one_paragraph(one):
    """Hello, world!"""


def multiple_paragraphs(one, two, three='default'):
    """Hello, world!

    Second paragraph *has formatting* and [http://example.com|link].
    It also refers to argument ``one`` using ``code`` style.
    This is still part of second paragraph.

    Third paragraph is _short_.

    Tags: tag, another tag
    """


def tables_alone():
    """
    | *a* | *b*   | *c*  |
    | 1st | table | here |

    | 2nd | table | has | only | one | row |

    Tags: another tag
    """


def preformatted():
    """
    | First block
    | has two lines

    | Second has only one

    Tags: TAG
    """


def lists(*list):
    """
    - first
    - second

    - another
    """


def hr():
    """
    ---
    ---

    ---------------
    """


def links():
    """
    - `Lists`, `One Paragraph`, `HR`, `hr`, `nön-äscïï`, `Special ½!"#¤%&/()=?<|>+-_.!~*'() chars`
    - `Section`, `Sub section with ääkköset`
    - `Shortcuts`, `keywords`, `LIBRARY intro duct ion`
    - http://robotframework.org
    - [http://robotframework.org|Robot Framework]
    """


def images():
    """
    https://github.com/robotframework/visual-identity/raw/master/logo/robot-framework.svg

    Images [https://github.com/robotframework/visual-identity/raw/master/logo/robot-framework.svg|title]
    inside paragraphs. This one is also a link:
    [https://github.com/robotframework/visual-identity/raw/master/logo/robot-framework.svg|
    https://github.com/robotframework/visual-identity/raw/master/logo/robot-framework.svg]
    """


@keyword('Nön-ÄSCÏÏ', tags=['Nön', 'äscïï', 'tägß'])
def non_ascii(ärg='ööööö'):
    """Älsö döc häs nön-äscïï stüff. Ïnclüdïng \u2603."""


@keyword('Special ½!"#¤%&/()=?<|>+-_.!~*\'() chars',
         tags=['½!"#¤%&/()=?', "<|>+-_.!~*\'()"])
def special_chars():
    """ Also doc has ½!"#¤%&/()=?<|>+-_.!~*'()."""


def zzz_long_documentation():
    """
    Last keyword has a bit longer documentation to make sure page moves
    when testing linking to keywords.

    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    - - -
    """
