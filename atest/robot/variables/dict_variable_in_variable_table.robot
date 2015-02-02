*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/dict_variable_in_variable_table.robot
Force Tags       regression    pybot    jybot
Resource         atest_resource.robot

*** Test Cases ***
Dict variable
    Check Test Case    ${TESTNAME}

First non-escaped equal sign is separator
    Check Test Case    ${TESTNAME}

Dict items must contain equal sign
    Check Test Case    ${TESTNAME}
    Variable creation should have failed    0    \&{NO EQUAL}
    ...    Dictionary item 'but not here' does not contain '=' separator.

Variables in key and value
    Check Test Case    ${TESTNAME}

Invalid key
    Check Test Case    ${TESTNAME}
    Variable creation should have failed    1    \&{INVALID KEY}
    ...    Creating dictionary failed: *

Non-dict cannot be used as dict variable
    Check Test Case    ${TESTNAME}
    Variable creation should have failed    2    \&{NON DICT AS DICT}
    ...    Value of variable '\&{LIST}' is not dictionary or dictionary-like.

*** Keywords ***
Variable creation should have failed
    [Arguments]    ${index}    ${name}    ${message}
    ${path} =    Normalize Path    ${DATADIR}/variables/dict_variable_in_variable_table.robot
    Check Log Message    @{ERRORS}[${index}]
    ...    Error in file '${path}': Setting variable '${name}' failed: ${message}
    ...    pattern=yes    level=ERROR
