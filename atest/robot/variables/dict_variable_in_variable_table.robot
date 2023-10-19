*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/dict_variable_in_variable_table.robot
Resource         atest_resource.robot

*** Test Cases ***
Dict variable
    Check Test Case    ${TESTNAME}

First non-escaped equal sign is separator
    Check Test Case    ${TESTNAME}

Equals is not detected in variable name
    Check Test Case    ${TESTNAME}

Invalid syntax
    Check Test Case    ${TESTNAME}
    Error In File    0    variables/dict_variable_in_variable_table.robot    16
    ...    SEPARATOR=\n
    ...    Setting variable '\&{BAD SYNTAX 1}' failed: Multiple errors:
    ...    - Invalid dictionary variable item 'this bad'. Items must use 'name=value' syntax or be dictionary variables themselves.
    ...    - Invalid dictionary variable item '\@{bad}'. Items must use 'name=value' syntax or be dictionary variables themselves.
    Error In File    1    variables/dict_variable_in_variable_table.robot    18
    ...    Setting variable '\&{BAD SYNTAX 2}' failed:
    ...    Invalid dictionary variable item 'bad\\=again'.
    ...    Items must use 'name=value' syntax or be dictionary variables themselves.

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
    Check Test Case    ${TESTNAME}

Dict from variable table should be dot-accessible
    Check Test Case    ${TESTNAME}

Dict from variable table should be dot-assignable
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Invalid key
    Check Test Case    ${TESTNAME}
    Error In File    5    variables/dict_variable_in_variable_table.robot    34
    ...    Setting variable '\&{NON HASHABLE KEY}' failed:
    ...    Creating dictionary variable failed: *

Non-dict cannot be used as dict variable
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3
    Error In File    2    variables/dict_variable_in_variable_table.robot    35
    ...    Setting variable '\&{NON DICT DICT 1}' failed:
    ...    Value of variable '\&{LIST}' is not dictionary or dictionary-like.
    Error In File    3    variables/dict_variable_in_variable_table.robot    36
    ...    Setting variable '\&{NON DICT DICT 2}' failed:
    ...    Value of variable '\&{SPACE}' is not dictionary or dictionary-like.
    Error In File    4    variables/dict_variable_in_variable_table.robot    37
    ...    Setting variable '\&{NON DICT DICT 3}' failed:
    ...    Value of variable '\&{EMPTY DICT.keys()}' is not dictionary or dictionary-like.
