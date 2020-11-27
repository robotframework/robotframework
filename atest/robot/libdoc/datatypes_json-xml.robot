*** Settings ***
Resource          libdoc_resource.robot
Default Tags      require-py3.7    require-py3.8    require-py3.9
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/DataTypesLibrary.json

*** Test Cases ***
Check DataType Enums
    DataType Enums Should Be    0
    ...    AssertionOperator
    ...    <p>This is some Doc</p>\n<p>This has was defined by assigning to __doc__.</p>
    ...    {"name": "equal","value": "=="}
    ...    {"name": "==","value": "=="}
    ...    {"name": "should be","value": "=="}
    ...    {"name": "inequal","value": "!="}
    ...    {"name": "!=","value": "!="}
    ...    {"name": "should not be","value": "!="}
    ...    {"name": "less than","value": "<"}
    ...    {"name": "<","value": "<"}
    ...    {"name": "greater than","value": ">"}
    ...    {"name": ">","value": ">"}
    ...    {"name": "<=","value": "<="}
    ...    {"name": ">=","value": ">="}
    ...    {"name": "contains","value": "*="}
    ...    {"name": "*=","value": "*="}
    ...    {"name": "starts","value": "^="}
    ...    {"name": "^=","value": "^="}
    ...    {"name": "should start with","value": "^="}
    ...    {"name": "ends","value": "$="}
    ...    {"name": "should end with","value": "$="}
    ...    {"name": "$=","value": "$="}
    ...    {"name": "matches","value": "$"}
    ...    {"name": "validate","value": "validate"}
    ...    {"name": "then","value": "then"}
    ...    {"name": "evaluate","value": "then"}

    DataType Enums Should Be    1
    ...    Small
    ...    <p>This is the Documentation.</p>\n<p>This was defined within the class definition.</p>
    ...    {"name": "one","value": "1"}
    ...    {"name": "two","value": "2"}
    ...    {"name": "three","value": "3"}
    ...    {"name": "four","value": "4"}

Check DataType TypedDict
    [Tags]    require-py3.9    require-py3.7
    DataType TypedDict Should Be    0
    ...    GeoLocation
    ...    <p>Defines the geolocation.</p>\n<ul>\n<li><code>latitude</code> Latitude between -90 and 90.</li>\n<li><code>longitude</code> Longitude between -180 and 180.</li>\n<li><code>accuracy</code> <b>Optional</b> Non-negative accuracy value. Defaults to 0. Example usage: <code>{'latitude': 59.95, 'longitude': 30.31667}</code></li>\n</ul>
    ...    {"key": "longitude", "type": "float", "required": "true"}
    ...    {"key": "latitude", "type": "float", "required": "true"}
    ...    {"key": "accuracy", "type": "float", "required": "false"}

Check DataType TypedDict
    [Tags]    require-py3.8
    DataType TypedDict Should Be    0
    ...    GeoLocation
    ...    <p>Defines the geolocation.</p>\n<ul>\n<li><code>latitude</code> Latitude between -90 and 90.</li>\n<li><code>longitude</code> Longitude between -180 and 180.</li>\n<li><code>accuracy</code> <b>Optional</b> Non-negative accuracy value. Defaults to 0. Example usage: <code>{'latitude': 59.95, 'longitude': 30.31667}</code></li>\n</ul>
    ...    {"key": "longitude", "type": "float"}
    ...    {"key": "latitude", "type": "float"}
    ...    {"key": "accuracy", "type": "float"}
