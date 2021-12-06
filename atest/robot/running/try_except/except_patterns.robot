*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/except_patterns.robot
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
