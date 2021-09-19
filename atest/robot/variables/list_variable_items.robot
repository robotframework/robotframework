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
    Check Test Case    ${TESTNAME} list
    Check Test Case    ${TESTNAME} string
    Check Test Case    ${TESTNAME} bytes

Invalid index using variable
    Check Test Case    ${TESTNAME}

Non-int index
    Check Test Case    ${TESTNAME} list
    Check Test Case    ${TESTNAME} string
    Check Test Case    ${TESTNAME} bytes

Non-int index using variable
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Empty index
    Check Test Case    ${TESTNAME} list
    Check Test Case    ${TESTNAME} string
    Check Test Case    ${TESTNAME} bytes

Invalid slice
    Check Test Case    ${TESTNAME} list
    Check Test Case    ${TESTNAME} string
    Check Test Case    ${TESTNAME} bytes

Non-int slice index
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2
    Check Test Case    ${TESTNAME} 3

Non-existing variable
    Check Test Case    ${TESTNAME}

Non-existing index variable
    Check Test Case    ${TESTNAME}

Non-subscriptable variable
    Check Test Case    ${TESTNAME}

List expansion using `@` syntax
    Check Test Case    ${TESTNAME}

List expansion fails if value is not list-like
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

List expansion with slice
    Check Test Case    ${TESTNAME}

List expansion with slice fails if value is not list-like
    Check Test Case    ${TESTNAME}

Object supporting both index and key access
    Check Test Case    ${TESTNAME}
