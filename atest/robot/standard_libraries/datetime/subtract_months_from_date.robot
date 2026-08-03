*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/subtract_months_from_date.robot
Resource         atest_resource.robot

*** Test Cases ***
Subtracting one month from a mid-month date
    Check Test Case    ${TESTNAME}

Subtracting using datetime input format
    Check Test Case    ${TESTNAME}

Subtracting 12 months lands on the prior year
    Check Test Case    ${TESTNAME}

Subtracting one month from Mar 31 clamps to Feb 29 (leap)
    Check Test Case    ${TESTNAME}

Subtracting one month from Mar 31 clamps to Feb 28 (non-leap)
    Check Test Case    ${TESTNAME}

Subtracting five months from Mar 31 lands on Oct 31
    Check Test Case    ${TESTNAME}

Negative subtraction adds months
    Check Test Case    ${TESTNAME}
