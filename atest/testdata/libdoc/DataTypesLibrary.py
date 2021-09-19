from enum import Enum, IntEnum
from typing import Optional, Union, Dict, Any, List


try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict


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
        print(type(credentials))

    def set_location(self, location: GeoLocation):
        pass

    def assert_something(self, value, operator: Optional[AssertionOperator] = None, exp: str = 'something?'):
        """This links to `AssertionOperator` .

        This is the next Line that links to 'Set Location` .
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
                             None]] = AssertionOperator.equal):
        pass

    def typing_types(self, list_of_str: List[str], dict_str_int: Dict[str, int], Whatever: Any, *args: List[Any]):
        pass
