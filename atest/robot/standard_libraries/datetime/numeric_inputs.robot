*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/numeric_inputs.robot
Resource         atest_resource.robot

*** Test Cases ***
Non-finite time inputs
    Check Test Case    ${TESTNAME}

Non-finite times fail before formatting or rounding
    Check Test Case    ${TESTNAME}

Integers too large for time conversion
    Check Test Case    ${TESTNAME}

Time arithmetic producing infinity
    Check Test Case    ${TESTNAME}

Non-finite epoch inputs
    Check Test Case    ${TESTNAME}

Epoch inputs outside supported range
    Check Test Case    ${TESTNAME}

Date calculations use timedelta range error
    Check Test Case    ${TESTNAME}

Date arithmetic outside supported range
    Check Test Case    ${TESTNAME}

Rounding outside supported date range
    Check Test Case    ${TESTNAME}

Finite numeric inputs still work
    Check Test Case    ${TESTNAME}
