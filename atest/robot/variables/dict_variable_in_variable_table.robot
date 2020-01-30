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
    Error In File    0    variables/dict_variable_in_variable_table.robot    15
    ...    Setting variable '\&{NO EQUAL}' failed:
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
    Error In File    4    variables/dict_variable_in_variable_table.robot    31
    ...    Setting variable '\&{NON HASHABLE KEY}' failed:
    ...    Creating dictionary failed: *

Non-dict cannot be used as dict variable
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3
    Error In File    1    variables/dict_variable_in_variable_table.robot    32
    ...    Setting variable '\&{NON DICT DICT 1}' failed:
    ...    Value of variable '\&{LIST}' is not dictionary or dictionary-like.
    Error In File    2    variables/dict_variable_in_variable_table.robot    33
    ...    Setting variable '\&{NON DICT DICT 2}' failed:
    ...    Value of variable '\&{SPACE}' is not dictionary or dictionary-like.
    Error In File    3    variables/dict_variable_in_variable_table.robot    34
    ...    Setting variable '\&{NON DICT DICT 3}' failed:
    ...    Value of variable '\&{EMPTY DICT.keys()}' is not dictionary or dictionary-like.
