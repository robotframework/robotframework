*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/except_behaviour.robot
Test Template     Verify try except and block statuses

*** Test Cases ***
Equals is the default matcher
    FAIL    PASS

Equals with whitespace
    FAIL    PASS

Glob matcher
    FAIL    NOT RUN    PASS

Glob with leading whitespace
    FAIL    PASS

Startswith matcher
    FAIL    PASS

Regexp matcher
    FAIL    NOT RUN    PASS

Regexp escapes
    FAIL    PASS

Variable in pattern
    FAIL    PASS

Invalid variable in pattern
    FAIL    NOT RUN    PASS    tc_status=FAIL

Matcher type cannot be defined with variable
    [Template]    NONE
    ${tc}=    Verify try except and block statuses    FAIL    PASS
    Block statuses should be    ${tc.body[1]}    FAIL    NOT RUN

Skip cannot be caught
    [Template]    NONE
    Verify try except and block statuses    SKIP    NOT RUN    PASS    tc_status=SKIP

Return cannot be caught
    [Template]    NONE
    Verify try except and block statuses    PASS   NOT RUN    PASS    path=body[0].body[0]

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
