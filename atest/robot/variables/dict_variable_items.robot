*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    variables/dict_variable_items.robot
Resource         atest_resource.robot

*** Test Cases ***
Valid key
    Check Test Case    ${TESTNAME}

Valid index using variable
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

Old syntax with `&` still works like earlier
    [Documentation]    `${dict}[key]` and `&{dict}[key]` work same way still.
    ...                In the future latter is deprecated and then changed.
    Check Test Case    ${TESTNAME}
