*** Settings ***
Resource          libdoc_resource.robot
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/DataTypesLibrary.json

*** Test Cases ***
Enum
    DataType Enum Should Be    0
    ...    AssertionOperator
    ...    <p>This is some Doc</p>\n<p>This has was defined by assigning to __doc__.</p>
    ...    {"name": "equal","value": "=="}
    ...    {"name": "==","value": "=="}
    ...    {"name": "<","value": "<"}
    ...    {"name": ">","value": ">"}
    ...    {"name": "<=","value": "<="}
    ...    {"name": ">=","value": ">="}
    DataType Enum Should Be    1
    ...    Small
    ...    <p>This is the Documentation.</p>\n<p>This was defined within the class definition.</p>
    ...    {"name": "one","value": "1"}
    ...    {"name": "two","value": "2"}
    ...    {"name": "three","value": "3"}
    ...    {"name": "four","value": "4"}

TypedDict
    DataType TypedDict Should Be    0
    ...    GeoLocation
    ...    <p>Defines the geolocation.</p>\n<ul>\n<li><code>latitude</code> Latitude between -90 and 90.</li>\n<li><code>longitude</code> Longitude between -180 and 180.</li>\n<li><code>accuracy</code> <b>Optional</b> Non-negative accuracy value. Defaults to 0.</li>\n</ul>\n<p>Example usage: <code>{'latitude': 59.95, 'longitude': 30.31667}</code></p>
    ...    {"key": "longitude", "type": "float", "required": "true"}
    ...    {"key": "latitude", "type": "float", "required": "true"}
    ...    {"key": "accuracy", "type": "float", "required": "false"}

Custom
    DataType Custom Should Be    0
    ...    CustomType
    ...    <p>Converter method doc is used when defined.</p>
    DataType Custom Should Be    1
    ...    CustomType2
    ...    <p>Class doc is used when converter method has no doc.</p>

Standard
    DataType Standard Should Be    0
    ...    Any
    ...    <p>Any value is accepted. No conversion is done.</p>
    DataType Standard Should Be    1
    ...    boolean
    ...    <p>Strings <code>TRUE</code>,
    DataType Standard Should Be    6
    ...    Literal
    ...    <p>Only specified values are accepted.

Standard with generics
    DataType Standard Should Be    2
    ...    dictionary
    ...    <p>Strings must be Python <a
    DataType Standard Should Be    5
    ...    list
    ...    <p>Strings must be Python <a

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
    Typedoc links should be    2    0    Union:
    ...    bool:boolean    int:integer    float    str:string    AssertionOperator    Small    GeoLocation    None
    Typedoc links should be    4    0    List:list
    ...    str:string
    Typedoc links should be    4    1    Dict:dictionary
    ...    str:string    int:integer
    Typedoc links should be    4    2    Any
    Typedoc links should be    4    3    List:list
    ...    Any
