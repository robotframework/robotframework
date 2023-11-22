*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/collections/dictionaries_should_be_equal.robot
Resource          atest_resource.robot

*** Test Cases ***
Comparison with itself
    Check Test Case    ${TESTNAME}

Keys in different order
    Check Test Case    ${TESTNAME}

Different dictionary types
    Check Test Case    ${TESTNAME}

First dictionary missing keys
    Check Test Case    ${TESTNAME}

Second dictionary missing keys
    Check Test Case    ${TESTNAME}

Both dictionaries missing keys
    Check Test Case    ${TESTNAME}

Missing keys and custom error message
    Check Test Case    ${TESTNAME}

Missing keys and custom error message with values
    Check Test Case    ${TESTNAME}

Different values
    Check Test Case    ${TESTNAME}

Different values and custom error message
    Check Test Case    ${TESTNAME}

Different values and custom error message with values
    Check Test Case    ${TESTNAME}

`ignore_keys`
    Check Test Case    ${TESTNAME}

`ignore_keys` with non-string keys
    Check Test Case    ${TESTNAME}

`ignore_keys` recursive
    Check Test Case    ${TESTNAME}

`ignore_keys` with missing keys
    Check Test Case    ${TESTNAME}

`ignore_keys` with wrong values
    Check Test Case    ${TESTNAME}

`ignore_keys` as string must be valid expression
    Check Test Case    ${TESTNAME}

`ignore_keys` must be list
    Check Test Case    ${TESTNAME}

`ignore_case`
    Check Test Case    ${TESTNAME}

`ignore_case` with ´ignore_keys`
    Check Test Case    ${TESTNAME}

`ignore_case` when normalized keys have conflict
    Check Test Case    ${TESTNAME}
