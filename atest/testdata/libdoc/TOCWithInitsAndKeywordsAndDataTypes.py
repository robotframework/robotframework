from enum import Enum


class Small(Enum):
    one = 1
    two = 2
    three = 3
    four = 4


AssertionOperator = Enum(
    "AssertionOperator",
    {
        "equal": "==",
        "==": "==",
        "should be": "==",
        "inequal": "!=",
        "!=": "!=",
        "should not be": "!=",
        "less than": "<",
        "<": "<",
        "greater than": ">",
        ">": ">",
        "<=": "<=",
        ">=": ">=",
        "contains": "*=",
        "*=": "*=",
        "starts": "^=",
        "^=": "^=",
        "should start with": "^=",
        "ends": "$=",
        "should end with": "$=",
        "$=": "$=",
        "matches": "$",
        "validate": "validate",
        "then": "then",
        "evaluate": "then",
    },
)
AssertionOperator.__doc__ = """This is some Doc"""


class TOCWithInitsAndKeywordsAndDataTypes:
    """
    = First entry =

    TOC in somewhat strange place.

        %TOC%

    = Second =

             = 3 =

    %TOC% not replaced here
    """

    def __init__(self, arg=True, enum: Small = Small.three):
        pass

    def keyword(self, assertion: AssertionOperator = AssertionOperator.equal, small: Small = Small.one):
        """Tags: tag"""
        pass
