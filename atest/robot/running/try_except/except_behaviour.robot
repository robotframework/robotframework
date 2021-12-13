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

Regexp escapes
    FAIL    PASS

Variable in pattern
    FAIL    PASS

Matcher type cannot be defined with variable
    [Template]
    ${tc}=    Verify try except and block statuses    FAIL    PASS
    Block statuses should be    ${tc.body[1]}    FAIL    NOT RUN

Skip cannot be caught
    [Template]
    Verify try except and block statuses    SKIP    NOT RUN    PASS    tc_status=SKIP

Return cannot be caught
    [Template]
    Verify try except and block statuses in uk    PASS   NOT RUN    PASS

AS gets the message
    FAIL    PASS

AS with multiple pattern
    FAIL    PASS

AS with many failures
    FAIL    PASS

AS with default except
    FAIL    PASS

AS as the error message
    FAIL    PASS
