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
    Verify Error    0    [ LIST__inv_list | not a list ]    \@{inv_list}
    ...    Expected list-like value, got string.

Invalid dict
    Check Test Case    ${TESTNAME}
    Verify Error    1    [ DICT__inv_dict | [*'1', *'2', 3] ]    \&{inv_dict}
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
    [Arguments]    ${index}    ${args}    ${var}    ${error}
    ${p1} =    Normalize Path    ${DATADIR}/variables/list_and_dict_from_variable_file.robot
    ${p2} =    Normalize Path    ${DATADIR}/variables/list_and_dict_variable_file.py
    ${error} =    Catenate    Error in file '${p1}':
    ...    Processing variable file '${p2}' with arguments ${args} failed:
    ...    Invalid variable '${var}': ${error}
    Check Log Message    @{ERRORS}[${index}]    ${error}    ERROR    pattern=yes
