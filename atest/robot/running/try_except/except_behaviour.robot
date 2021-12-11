*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/except_behaviour.robot
Test Template     Verify try except and block statuses

*** Test Cases ***
Equals is the default matcher
    FAIL    PASS

Glob matcher
    FAIL    PASS

Startswith matcher
    FAIL    PASS

Regexp matcher
    FAIL    PASS

Variable in pattern
    FAIL    PASS

Return cannot be catch
    [Template]
    Check test case    ${TEST NAME}

AS get the message
    FAIL    PASS

AS with many failures
    FAIL    PASS
