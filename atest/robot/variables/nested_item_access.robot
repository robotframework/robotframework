*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/nested_item_access.robot
Resource         atest_resource.robot

*** Test Cases ***
Nested list access
    Check Test Case    ${TESTNAME}

Nested dict access
    Check Test Case    ${TESTNAME}

Nested mixed access
    Check Test Case    ${TESTNAME}

Nested access with slicing
    Check Test Case    ${TESTNAME}

Non-existing nested list item
    Check Test Case    ${TESTNAME}

Non-existing nested dict item
    Check Test Case    ${TESTNAME}

Invalid nested list access
    Check Test Case    ${TESTNAME}

Invalid nested dict access
    Check Test Case    ${TESTNAME}

Nested access with non-list/dict
    Check Test Case    ${TESTNAME}

Escape nested
    Check Test Case    ${TESTNAME}

Nested access doesn't support old `@` and `&` syntax
    Check Test Case    ${TESTNAME}
