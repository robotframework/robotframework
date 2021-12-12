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

Skip cannot be catch
    [Template]
    Verify try except and block statuses    SKIP    NOT RUN    PASS    tc_status=SKIP

Return cannot be catch
    [Template]
    Verify try except and block statuses in uk    PASS   NOT RUN    PASS

AS gets the message
    FAIL    PASS

AS with many failures
    FAIL    PASS

AS with default except
    FAIL    PASS
