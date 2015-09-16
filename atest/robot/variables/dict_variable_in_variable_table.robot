*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/dict_variable_in_variable_table.robot
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

Extended variables
    Check Test Case    ${TESTNAME}

Internal variables
    Check Test Case    ${TESTNAME}

Last item overrides
    Check Test Case    ${TESTNAME}

Create from dict variable
    Check Test Case    ${TESTNAME}

Dict from variable table should be ordered
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Dict from variable table should be dot-accessible
    Check Test Case    ${TESTNAME}

Dict from variable table should be dot-assignable
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Invalid key
    Check Test Case    ${TESTNAME}
    Variable creation should have failed    4    \&{NON HASHABLE KEY}
    ...    Creating dictionary failed: *

Non-dict cannot be used as dict variable
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3
    Variable creation should have failed    1    \&{NON DICT DICT 1}
    ...    Value of variable '\&{LIST}' is not dictionary or dictionary-like.
    Variable creation should have failed    2    \&{NON DICT DICT 2}
    ...    Value of variable '\&{SPACE}' is not dictionary or dictionary-like.
    Variable creation should have failed    3    \&{NON DICT DICT 3}
    ...    Value of variable '\&{EMPTY DICT.keys()}' is not dictionary or dictionary-like.

*** Keywords ***
Variable creation should have failed
    [Arguments]    ${index}    ${name}    ${message}
    ${path} =    Normalize Path    ${DATADIR}/variables/dict_variable_in_variable_table.robot
    Check Log Message    @{ERRORS}[${index}]
    ...    Error in file '${path}': Setting variable '${name}' failed: ${message}
    ...    pattern=yes    level=ERROR
