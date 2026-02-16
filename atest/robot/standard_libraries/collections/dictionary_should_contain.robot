*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/collections/dictionary_should_contain.robot
Resource          atest_resource.robot

*** Test Cases ***
Should contain key
    Check Test Case    ${TESTNAME}

Should contain key with custom message
    Check Test Case    ${TESTNAME}

Should contain key with `ignore_case`
    Check Test Case    ${TESTNAME}

Should not contain key
    Check Test Case    ${TESTNAME}

Should not contain key with custom message
    Check Test Case    ${TESTNAME}

Should not contain key with `ignore_case`
    Check Test Case    ${TESTNAME}

Should contain value
    Check Test Case    ${TESTNAME}

Should contain value with custom message
    Check Test Case    ${TESTNAME}

Should contain value with `ignore_case`
    Check Test Case    ${TESTNAME}

Should not contain value
    Check Test Case    ${TESTNAME}

Should not contain value with custom message
    Check Test Case    ${TESTNAME}

Should not contain value with `ignore_case`
    Check Test Case    ${TESTNAME}

Should contain item
    Check Test Case    ${TESTNAME}

Should contain item with missing key
    Check Test Case    ${TESTNAME}

Should contain item with missing key and custom message
    Check Test Case    ${TESTNAME}

Should contain item with wrong value
    Check Test Case    ${TESTNAME}

Should contain item with wrong value and custom message
    Check Test Case    ${TESTNAME}

Should contain item with values looking same but having different types
    Check Test Case    ${TESTNAME}

Should contain item with `ignore_case`
    Check Test Case    ${TESTNAME}

Should contain item with `ignore_case=key`
    Check Test Case    ${TESTNAME}

Should contain item with `ignore_case=value`
    Check Test Case    ${TESTNAME}

Should contain sub dictionary
    Check Test Case    ${TESTNAME}

Should contain sub dictionary with missing keys
    Check Test Case    ${TESTNAME}

Should contain sub dictionary with missing keys and custom error message
    Check Test Case    ${TESTNAME}

Should contain sub dictionary with missing keys and custom error message containig values
    Check Test Case    ${TESTNAME}

Should contain sub dictionary with wrong value
    Check Test Case    ${TESTNAME}

Should contain sub dictionary with wrong value and custom error message
    Check Test Case    ${TESTNAME}

Should contain sub dictionary with wrong value and custom error message containing values
    Check Test Case    ${TESTNAME}

Should contain sub dictionary with deprecated NO VALUES
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc[0, 0]}   Using 'NO VALUES' for disabling the 'values' argument is deprecated. Use 'values=False' instead.    WARN

Should contain sub dictionary with `ignore_case`
    Check Test Case    ${TESTNAME}

`ignore_case` when normalized keys have conflict
    Check Test Case    ${TESTNAME}

`has_key` is not required
    Check Test Case    ${TESTNAME}

Should contain sub dictionary with `ignore_value_order`
    Check Test Case    ${TESTNAME}

Should contain sub dictionary with `ignore_value_order` set to False when dictionaries have lists in different order
    Check Test Case    ${TESTNAME}
