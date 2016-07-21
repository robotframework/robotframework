*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    standard_libraries/datetime/date_ranges.robot
Resource         atest_resource.robot

*** Test Cases ***
Date is not altered
    Check Test Case    ${TESTNAME}

Date is not altered during DST changes
    Check Test Case    ${TESTNAME}

Timestamps support years since 1900
    Check Test Case    ${TESTNAME}

Datetime supports years since 1
    Check Test Case    ${TESTNAME}

Epoch supports years since 1970
    Check Test Case    ${TESTNAME}

Too low year
    Check Test Case    ${TESTNAME}
