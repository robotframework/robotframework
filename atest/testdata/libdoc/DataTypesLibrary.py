from enum import Enum, IntEnum
from typing import Any, Dict, List, Literal, Optional, Union
try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict

from robot.api.deco import library


class HttpCredentials(TypedDict):
    username: str
    password: str


class _GeoCoordinated(TypedDict):
    longitude: float
    latitude: float


class GeoLocation(_GeoCoordinated, total=False):
    """Defines the geolocation.

    - ``latitude`` Latitude between -90 and 90.
    - ``longitude`` Longitude between -180 and 180.
    - ``accuracy`` *Optional* Non-negative accuracy value. Defaults to 0.

    Example usage: ``{'latitude': 59.95, 'longitude': 30.31667}``
    """
    accuracy: float


class Small(IntEnum):
    """This is the Documentation.

    This was defined within the class definition.
    """
    one = 1
    two = 2
    three = 3
    four = 4


AssertionOperator = Enum(
    "AssertionOperator",
    {
        "equal": "==",
        "==": "==",
        "<": "<",
        ">": ">",
        "<=": "<=",
        ">=": ">="
    },
)
AssertionOperator.__doc__ = """This is some Doc

This has was defined by assigning to __doc__."""


class CustomType:
    """This doc not used because converter method has doc."""
    @classmethod
    def parse(cls, value: Union[str, int]):
        """Converter method doc is used when defined."""
        return value


class CustomType2:
    """Class doc is used when converter method has no doc."""
    def __init__(self, value):
        self.value = value


class Unknown:
    pass


class A:
    @classmethod
    def not_used_converter_should_not_be_documented(cls, value):
        return 1


@library(converters={CustomType: CustomType.parse,
                     CustomType2: CustomType2,
                     A: A.not_used_converter_should_not_be_documented},
         auto_keywords=True)
class DataTypesLibrary:
    """This Library has Data Types.

    It has some in ``__init__`` and others in the `Keywords`.

    The DataTypes are the following that should be linked.
    `HttpCredentials` , `GeoLocation` , `Small` and `AssertionOperator`.
    """

    def __init__(self, credentials: Small = Small.one):
        """This is the init Docs.

        It links to `Set Location` keyword and to `GeoLocation` data type.
        """
        pass

    def set_location(self, location: GeoLocation) -> bool:
        return True

    def assert_something(self, value, operator: Optional[AssertionOperator] = None, exp: str = 'something?'):
        """This links to `AssertionOperator` .

        This is the next Line that links to `Set Location` .
        """
        pass

    def funny_unions(self,
                     funny: Union[
                         bool,
                         Union[
                             int,
                             float,
                             bool,
                             str,
                             AssertionOperator,
                             Small,
                             GeoLocation,
                             None]] = AssertionOperator.equal) -> Union[int, List[int]]:
        pass

    def typing_types(self, list_of_str: List[str], dict_str_int: Dict[str, int], whatever: Any, *args: List[Any]):
        pass

    def x_literal(self, arg: Literal[1, 'xxx', b'yyy', True, None, Small.one]):
        pass

    def custom(self, arg: CustomType, arg2: 'CustomType2', arg3: CustomType, arg4: Unknown):
        pass
