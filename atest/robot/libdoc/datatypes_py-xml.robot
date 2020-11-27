*** Settings ***
Resource          libdoc_resource.robot
Force Tags      require-py3.7
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/DataTypesLibrary.py

*** Test Cases ***
Check DataType Enums
    DataType Enums Should Be    0
    ...    AssertionOperator
    ...    This is some Doc\n\nThis has was defined by assigning to __doc__.
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
    ...    This is the Documentation.\n\n \ \ \ This was defined within the class definition.
    ...    {"name": "one","value": "1"}
    ...    {"name": "two","value": "2"}
    ...    {"name": "three","value": "3"}
    ...    {"name": "four","value": "4"}

Check DataType TypedDict
    ${typ_ext}=     Is Typing Extensions
    IF   ${typ_ext}
        DataType TypedDict Should Be    0
        ...    GeoLocation
        ...    Defines the geolocation.\n\n \ \ \ - ``latitude`` Latitude between -90 and 90.\n \ \ \ - ``longitude`` Longitude between -180 and 180.\n \ \ \ - ``accuracy`` *Optional* Non-negative accuracy value. Defaults to 0.\n \ \ \ Example usage: ``{'latitude': 59.95, 'longitude': 30.31667}``
        ...    {"key": "longitude", "type": "float", "required": "true"}
        ...    {"key": "latitude", "type": "float", "required": "true"}
        ...    {"key": "accuracy", "type": "float", "required": "false"}
    ELSE
        DataType TypedDict Should Be    0
        ...    GeoLocation
        ...    Defines the geolocation.\n\n \ \ \ - ``latitude`` Latitude between -90 and 90.\n \ \ \ - ``longitude`` Longitude between -180 and 180.\n \ \ \ - ``accuracy`` *Optional* Non-negative accuracy value. Defaults to 0.\n \ \ \ Example usage: ``{'latitude': 59.95, 'longitude': 30.31667}``
        ...    {"key": "longitude", "type": "float"}
        ...    {"key": "latitude", "type": "float"}
        ...    {"key": "accuracy", "type": "float"}
    END
