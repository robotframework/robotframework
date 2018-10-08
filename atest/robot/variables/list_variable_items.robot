*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/list_variable_items.robot
Resource         atest_resource.robot

*** Test Cases ***
Valid index
    Check Test Case    ${TESTNAME}

Valid index using variable
    Check Test Case    ${TESTNAME}

Slicing
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

Old syntax with `@` still works like earlier
    [Documentation]    `${list}[1]` and `@{list}[1]` work same way still.
    ...                In the future latter is deprecated and changed.
    Check Test Case    ${TESTNAME}

Old syntax with `@` doesn't support new slicing syntax
    [Documentation]    Slicing support should be added in RF 3.3 when `@{list}[index]` changes.
    Check Test Case    ${TESTNAME}
