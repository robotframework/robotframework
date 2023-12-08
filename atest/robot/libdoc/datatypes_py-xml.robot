*** Settings ***
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/DataTypesLibrary.py
Resource          libdoc_resource.robot

*** Test Cases ***
Enum
    DataType Enum Should Be    0
    ...    AssertionOperator
    ...    This is some Doc\n\nThis has was defined by assigning to __doc__.
    ...    {"name": "equal","value": "=="}
    ...    {"name": "==","value": "=="}
    ...    {"name": "<","value": "<"}
    ...    {"name": ">","value": ">"}
    ...    {"name": "<=","value": "<="}
    ...    {"name": ">=","value": ">="}
    DataType Enum Should Be    1
    ...    Small
    ...    This is the Documentation.\n\nThis was defined within the class definition.
    ...    {"name": "one","value": "1"}
    ...    {"name": "two","value": "2"}
    ...    {"name": "three","value": "3"}
    ...    {"name": "four","value": "4"}

TypedDict
    ${required}     Get Element Count    ${LIBDOC}    xpath=dataTypes/typedDicts/typedDict/items/item[@required]
    IF   $required == 0
        DataType TypedDict Should Be    0
        ...    GeoLocation
        ...    Defines the geolocation.\n\n- ``latitude`` Latitude between -90 and 90.\n- ``longitude`` Longitude between -180 and 180.\n- ``accuracy`` *Optional* Non-negative accuracy value. Defaults to 0.\n\nExample usage: ``{'latitude': 59.95, 'longitude': 30.31667}``
        ...    {"key": "longitude", "type": "float"}
        ...    {"key": "latitude", "type": "float"}
        ...    {"key": "accuracy", "type": "float"}
    ELSE
        DataType TypedDict Should Be    0
        ...    GeoLocation
        ...    Defines the geolocation.\n\n- ``latitude`` Latitude between -90 and 90.\n- ``longitude`` Longitude between -180 and 180.\n- ``accuracy`` *Optional* Non-negative accuracy value. Defaults to 0.\n\nExample usage: ``{'latitude': 59.95, 'longitude': 30.31667}``
        ...    {"key": "longitude", "type": "float", "required": "true"}
        ...    {"key": "latitude", "type": "float", "required": "true"}
        ...    {"key": "accuracy", "type": "float", "required": "false"}
    END

Custom
    DataType Custom Should Be    0
    ...    CustomType
    ...    Converter method doc is used when defined.
    DataType Custom Should Be    1
    ...    CustomType2
    ...    Class doc is used when converter method has no doc.

Standard
    DataType Standard Should Be    0
    ...    Any
    ...    Any value is accepted. No conversion is done.
    DataType Standard Should Be    1
    ...    boolean
    ...    Strings ``TRUE``, ``YES``, ``ON`` and ``1`` are converted to Boolean ``True``,
    DataType Standard Should Be    6
    ...    Literal
    ...    Only specified values are accepted.

Standard with generics
    DataType Standard Should Be    2
    ...    dictionary
    ...    Strings must be Python [[]https://docs.python.org/library/stdtypes.html#dict|dictionary]
    DataType Standard Should Be    5
    ...    list
    ...    Strings must be Python [[]https://docs.python.org/library/stdtypes.html#list|list]

Accepted types
    Accepted Types Should Be    0     Standard     Any
    ...    Any
    Accepted Types Should Be    2     Standard     boolean
    ...    string    integer    float    None
    Accepted Types Should Be    10    Standard     Literal
    ...    Any
    Accepted Types Should Be    3     Custom       CustomType
    ...    string    integer
    Accepted Types Should Be    4     Custom       CustomType2
    Accepted Types Should Be    7     TypedDict    GeoLocation
    ...    string    Mapping
    Accepted Types Should Be    1     Enum         AssertionOperator
    ...    string
    Accepted Types Should Be    12    Enum         Small
    ...    string    integer

Usages
    Usages Should Be    0     Standard     Any
    ...    Typing Types
    Usages Should Be    5     Standard     dictionary
    ...    Typing Types
    Usages Should Be    13    Standard    string
    ...    Assert Something    Funny Unions    Typing Types
    Usages Should Be    3     Custom       CustomType
    ...    Custom
    Usages Should be    7     TypedDict    GeoLocation
    ...    Funny Unions    Set Location
    Usages Should Be    12    Enum         Small
    ...    __init__    Funny Unions

Typedoc links in arguments
    Typedoc links should be    0    1    Union:
    ...    AssertionOperator    None
    Typedoc links should be    0    2    str:string
    Typedoc links should be    1    0    CustomType
    Typedoc links should be    1    1    CustomType2
    Typedoc links should be    1    2    CustomType
    Typedoc links should be    1    3    Unknown:
    Typedoc links should be    2    0    Union:
    ...    bool:boolean    int:integer    float    str:string    AssertionOperator    Small    GeoLocation    None
    Typedoc links should be    4    0    List:list
    ...    str:string
    Typedoc links should be    4    1    Dict:dictionary
    ...    str:string    int:integer
    Typedoc links should be    4    2    Any
    Typedoc links should be    4    3    List:list
    ...    Any
