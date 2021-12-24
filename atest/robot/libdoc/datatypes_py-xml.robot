*** Settings ***
Resource          libdoc_resource.robot
Suite Setup       Run Libdoc And Parse Output    ${TESTDATADIR}/DataTypesLibrary.py

*** Test Cases ***
Enum
    DataType Enums Should Be    0
    ...    AssertionOperator
    ...    This is some Doc\n\nThis has was defined by assigning to __doc__.
    ...    {"name": "equal","value": "=="}
    ...    {"name": "==","value": "=="}
    ...    {"name": "<","value": "<"}
    ...    {"name": ">","value": ">"}
    ...    {"name": "<=","value": "<="}
    ...    {"name": ">=","value": ">="}
    DataType Enums Should Be    1
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
