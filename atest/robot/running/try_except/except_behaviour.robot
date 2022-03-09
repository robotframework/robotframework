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

Startswith matcher
    FAIL    PASS

Regexp matcher
    FAIL    NOT RUN    PASS

Regexp escapes
    FAIL    PASS

Regexp flags
    FAIL    NOT RUN    PASS

Variable in pattern
    FAIL    PASS

Invalid variable in pattern
    FAIL    FAIL    PASS

Non-string pattern
    FAIL    NOT RUN    NOT RUN    NOT RUN    NOT RUN

Variable in pattern type
    FAIL    PASS

Invalid variable in pattern type
    FAIL    FAIL    PASS

Invalid pattern type
    FAIL    FAIL

Non-string pattern type
    FAIL    FAIL

Pattern type without patterns
    FAIL    PASS

Skip cannot be caught
    SKIP    NOT RUN    PASS    tc_status=SKIP

Return cannot be caught
    PASS    NOT RUN    PASS       path=body[0].body[0]

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
