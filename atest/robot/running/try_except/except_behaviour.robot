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

Regexp flags
    FAIL    NOT RUN    PASS

Variable in pattern
    FAIL    PASS

Invalid variable in pattern
    FAIL    NOT RUN    PASS       tc_status=FAIL

Matcher type cannot be defined with variable
    FAIL    PASS       NOT RUN    tc_status=FAIL    path=body[0]
    FAIL    NOT RUN               tc_status=FAIL    path=body[1]

Skip cannot be caught
    SKIP    NOT RUN    PASS       tc_status=SKIP

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
