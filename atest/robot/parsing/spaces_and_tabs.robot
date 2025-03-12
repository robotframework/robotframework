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
    Check Log Message    ${tc[0, 0]}    No spaces at end
    Check Log Message    ${tc[1, 0]}    One space at end
    Check Log Message    ${tc[2, 0]}    Two spaces at end
    Check Log Message    ${tc[3, 0]}    Ten spaces at end
    Check Log Message    ${tc[4, 0]}    Tab at end

Tabs
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    I ignore tabs    DEBUG

Tabs and spaces
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc[0, 0]}    I ignore tabs (and spaces)    DEBUG
