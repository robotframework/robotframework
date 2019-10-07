*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/dict_variable_items.robot
Resource         atest_resource.robot

*** Test Cases ***
Valid key
    Check Test Case    ${TESTNAME}

Valid key with square brackets
    Check Test Case    ${TESTNAME}

Unmatched square brackets
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3

Index with variable
    Check Test Case    ${TESTNAME}

Index with variable using item access
    Check Test Case    ${TESTNAME}

Values can be mutated
    Check Test Case    ${TESTNAME}

List-like values are not manipulated
    Check Test Case    ${TESTNAME}

Integer key cannot be accessed as string
    Check Test Case    ${TESTNAME}

String key cannot be accessed as integer
    Check Test Case    ${TESTNAME}

Invalid key
    Check Test Case    ${TESTNAME}

Invalid key using variable
    Check Test Case    ${TESTNAME}

Non-hashable key
    Check Test Case    ${TESTNAME}

Non-existing variable
    Check Test Case    ${TESTNAME}

Non-existing index variable
    Check Test Case    ${TESTNAME}

Non-dict variable
    Check Test Case    ${TESTNAME}

Sanity check
    Check Test Case    ${TESTNAME}

Old syntax with `&` still works but is deprecated
    [Documentation]    `${dict}[key]` and `&{dict}[key]` work same way still.
    ...                In the future latter is deprecated and then changed.
    ${tc} =    Check Test Case    ${TESTNAME}
    Old item access syntax is deprecated    ${tc.kws[0].msgs[0]}    \&{DICT}[A]
    Old item access syntax is deprecated    ${ERRORS[0]}            \&{DICT}[A]
    Old item access syntax is deprecated    ${tc.kws[1].msgs[0]}    \&{DICT}[\${1}]
    Old item access syntax is deprecated    ${ERRORS[1]}            \&{DICT}[\${1}]
    Old item access syntax is deprecated    ${tc.kws[2].msgs[0]}    \&{DICT}[nonex]
    Old item access syntax is deprecated    ${ERRORS[2]}            \&{DICT}[nonex]

*** Keywords ***
Old item access syntax is deprecated
    [Arguments]    ${msg}    ${deprecated}
    Check log message    ${msg}
    ...    Accessing variable items using '${deprecated}' syntax is deprecated. Use '$${deprecated[1:]}' instead.
    ...    WARN
