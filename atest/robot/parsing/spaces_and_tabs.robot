*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    parsing/spaces_and_tabs.robot
Resource         atest_resource.robot

*** Test Cases ***
Minimum spaces
    Check Test Case    ${TESTNAME}

Inconsistent indentation
    Check Test Case    ${TESTNAME}

Lot of spaces
    Check Test Case    ${TESTNAME}

Trailing spaces
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    No spaces at end
    Check Log Message    ${tc.kws[1].msgs[0]}    One space at end
    Check Log Message    ${tc.kws[2].msgs[0]}    Two spaces at end
    Check Log Message    ${tc.kws[3].msgs[0]}    Ten spaces at end
    Check Log Message    ${tc.kws[4].msgs[0]}    Tab at end

Tabs
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    I ignore tabs    DEBUG

Tabs and spaces
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    I ignore tabs (and spaces)    DEBUG
