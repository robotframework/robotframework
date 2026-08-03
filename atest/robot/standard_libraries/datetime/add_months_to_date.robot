*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/add_months_to_date.robot
Resource         atest_resource.robot

*** Test Cases ***
Adding one month to a mid-month date
    Check Test Case    ${TESTNAME}

Adding one month using datetime input format
    Check Test Case    ${TESTNAME}

Adding multiple months crosses a year boundary
    Check Test Case    ${TESTNAME}

Adding ten months to Mar 31 lands on Jan 31 the year after next
    Check Test Case    ${TESTNAME}

Adding one month to Jan 31 clamps to Feb 29 in a leap year
    Check Test Case    ${TESTNAME}

Adding one month to Jan 31 clamps to Feb 28 in a non-leap year
    Check Test Case    ${TESTNAME}

Adding one month to Mar 31 clamps to Apr 30
    Check Test Case    ${TESTNAME}

Adding a negative month subtracts months
    Check Test Case    ${TESTNAME}

Subtracting two months from Mar 31 yields Jan 31
    Check Test Case    ${TESTNAME}

Large positive month delta spans many years
    Check Test Case    ${TESTNAME}
