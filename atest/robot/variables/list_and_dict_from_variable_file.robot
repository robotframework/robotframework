*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/list_and_dict_from_variable_file.robot
Resource         atest_resource.robot

*** Test Cases ***
Valid list
    Check Test Case    ${TESTNAME}

Valid dict
    Check Test Case    ${TESTNAME}

List is list
    Check Test Case    ${TESTNAME}

Dict is dotted
    Check Test Case    ${TESTNAME}

Dict is ordered
    Check Test Case    ${TESTNAME}

Invalid list
    Check Test Case    ${TESTNAME}
    Verify Error    0    3
    ...    [ LIST__inv_list | not a list ]
    ...    \@{inv_list}
    ...    Expected list-like value, got string.

Invalid dict
    Check Test Case    ${TESTNAME}
    Verify Error    1    4
    ...    [ DICT__inv_dict | ['1', '2', 3] ]
    ...    \&{inv_dict}
    ...    Expected dict-like value, got list.

Scalar list likes can be used as list
    Check Test Case    ${TESTNAME}

Scalar list likes are not converted to lists
    Check Test Case    ${TESTNAME}

Scalar dicts can be used as dicts
    Check Test Case    ${TESTNAME}

Scalar dicts are not converted to DotDicts
    Check Test Case    ${TESTNAME}

Failing list
    Check Test Case    ${TESTNAME}
    Check Test Case    ${TESTNAME} in for loop

Failing dict
    Check Test Case    ${TESTNAME}

Open files are not lists
    Check Test Case    ${TESTNAME}

Closed files are not lists
    Check Test Case    ${TESTNAME}

*** Keywords ***
Verify Error
    [Arguments]    ${index}    ${lineno}    ${args}    ${var}    ${error}
    ${path} =    Normalize Path    ${DATADIR}/variables/list_and_dict_variable_file.py
    Error In File    ${index}    variables/list_and_dict_from_variable_file.robot    ${lineno}
    ...    Processing variable file '${path}' with arguments ${args} failed:
    ...    Invalid variable '${var}': ${error}
    ...    pattern=False
