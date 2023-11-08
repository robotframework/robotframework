*** Settings ***
Documentation    Note that returning binary/bytes is tested in `binary_result.robot`.
Suite Setup      Run Remote Tests    return_values.robot    returnvalues.py
Resource         remote_resource.robot

*** Test Cases ***
String
    Check Test Case    ${TEST NAME}

Integer
    Check Test Case    ${TEST NAME}

Float
    Check Test Case    ${TEST NAME}

Boolean
    Check Test Case    ${TEST NAME}

Datetime
    Check Test Case    ${TEST NAME}

List
    Check Test Case    ${TEST NAME}

Dict
    Check Test Case    ${TEST NAME}
