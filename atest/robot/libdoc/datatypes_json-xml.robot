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

Usages
    Usages Should Be    1    Custom    CustomType
    ...    Custom=arg,arg3
    Usages Should be    3    TypedDict    GeoLocation
    ...    Funny Unions=funny
    ...    Set Location=location
    Usages Should Be    4    Enum    Small
    ...    __init__=credentials
    ...    Funny Unions=funny
