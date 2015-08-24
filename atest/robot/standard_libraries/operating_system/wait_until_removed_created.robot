*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/operating_system/wait_until_removed_created.robot
Force Tags      regression  jybot  pybot
Resource        atest_resource.robot

*** Test Cases ***
File And Dir Already Removed
    Check Test Case  File And Dir Already Removed

File And Dir Removed Before Timeout
    Check Test Case  File And Dir Removed Before Timeout

File And Dir Removed With Pattern
    Check Test Case  File And Dir Removed With Pattern

File Not Removed Before Timeout
    Check Test Case  File Not Removed Before Timeout

Dir Not Removed Before Timeout
    Check Test Case  Dir Not Removed Before Timeout

Not Removed Before Timeout With Pattern
    Check Test Case  Not Removed Before Timeout With Pattern

Invalid Remove Timeout
    Check Test Case  Invalid Remove Timeout

File And Dir Already Created
    Check Test Case  File And Dir Already Created

File And Dir Created Before Timeout
    Check Test Case  File And Dir Created Before Timeout

File And Dir Created With Pattern
    Check Test Case  File And Dir Created With Pattern

File Not Created Before Timeout
    Check Test Case  File Not Created Before Timeout

Dir Not Created Before Timeout
    Check Test Case  Dir Not Created Before Timeout

Not Created Before Timeout With Pattern
    Check Test Case  Not Created Before Timeout With Pattern

Invalid Create Timeout
    Check Test Case  Invalid Create Timeout

Wait Until File With Glob Like Name
    Check Test Case  ${TEST NAME}

Wait Until Removed File With Glob Like Name
    Check Test Case  ${TEST NAME}
