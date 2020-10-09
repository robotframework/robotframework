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

Dict expansion using `&` syntax
    Check Test Case    ${TESTNAME}

Dict expansion fails if value is not dict-like
    Check Test Case    ${TESTNAME}
