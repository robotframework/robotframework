*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/list_variable_items.robot
Resource         atest_resource.robot

*** Test Cases ***
Valid index
    Check Test Case    ${TESTNAME}

Index with variable
    Check Test Case    ${TESTNAME}

Index with variable using item access
    Check Test Case    ${TESTNAME}

Slicing
    Check Test Case    ${TESTNAME}

Slicing with variable
    Check Test Case    ${TESTNAME}

Invalid index
    Check Test Case    ${TESTNAME}

Invalid index using variable
    Check Test Case    ${TESTNAME}

Non-int index
    Check Test Case    ${TESTNAME}

Non-int index using variable
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Empty index
    Check Test Case    ${TESTNAME}

Invalid slice
    Check Test Case    ${TESTNAME}

Non-int slice index
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3

Non-existing variable
    Check Test Case    ${TESTNAME}

Non-existing index variable
    Check Test Case    ${TESTNAME}

Non-list variable
    Check Test Case    ${TESTNAME}

Old syntax with `@` still works but is deprecated
    [Documentation]    `${list}[1]` and `@{list}[1]` work same way still.
    ...                In the future latter is deprecated and changed.
    ${tc} =    Check Test Case    ${TESTNAME}
    Old item access syntax is deprecated    ${tc.kws[0].msgs[0]}    \@{LIST}[0]
    Old item access syntax is deprecated    ${ERRORS[0]}            \@{LIST}[0]
    Old item access syntax is deprecated    ${tc.kws[1].msgs[0]}    \@{LIST}[\${-1}]
    Old item access syntax is deprecated    ${ERRORS[1]}            \@{LIST}[\${-1}]
    Old item access syntax is deprecated    ${tc.kws[2].msgs[0]}    \@{LIST}[99]
    Old item access syntax is deprecated    ${ERRORS[2]}            \@{LIST}[99]

Old syntax with `@` doesn't support new slicing syntax
    [Documentation]    Slicing support should be added in RF 3.3 when `@{list}[index]` changes.
    Check Test Case    ${TESTNAME}

*** Keywords ***
Old item access syntax is deprecated
    [Arguments]    ${msg}    ${deprecated}
    Check log message    ${msg}
    ...    Accessing variable items using '${deprecated}' syntax is deprecated. Use '$${deprecated[1:]}' instead.
    ...    WARN
