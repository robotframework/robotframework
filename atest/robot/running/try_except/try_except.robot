*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/try_except.robot
Test Template     Verify try except and block statuses

*** Test Cases ***
Try with no failures
    PASS    NOT RUN

First except executed
    FAIL    PASS

Second except executed
    FAIL    NOT RUN    PASS    NOT RUN

Second matching except ignored
    FAIL    PASS    NOT RUN

Except handler failing
    FAIL    FAIL    NOT RUN

Else branch executed
    PASS    NOT RUN    PASS

Else branch not executed
    FAIL    PASS    NOT RUN

Else branch failing
    PASS    NOT RUN    FAIL

Multiple except patterns
    FAIL    PASS

Default except pattern
    FAIL    PASS

Syntax errors cannot be caught
    FAIL    NOT RUN    NOT RUN

Finally block executed when no failures
    [Template]    None
    ${tc}=   Verify try except and block statuses    PASS    NOT RUN    PASS    PASS
    Check Log Message    ${tc.body[0].body[0].body[0].msgs[0]}    all good
    Check Log Message    ${tc.body[0].body[2].body[0].msgs[0]}    in the else
    Check Log Message    ${tc.body[0].body[3].body[0].msgs[0]}    Hello from finally!

Finally block executed after catch
    [Template]    None
    ${tc}=   Verify try except and block statuses    FAIL    PASS    PASS
    Check Log Message    ${tc.body[0].body[0].body[0].msgs[0]}    all not good    FAIL
    Check Log Message    ${tc.body[0].body[1].body[0].msgs[0]}    we are safe now
    Check Log Message    ${tc.body[0].body[2].body[0].msgs[0]}    Hello from finally!

Finally block executed after failure in except
    FAIL    FAIL    NOT RUN   PASS

Finally block executed after failure in else
    PASS    NOT RUN    FAIL    PASS

Try finally with no errors
    PASS    PASS

Try finally with failing try
    FAIL    PASS    tc_status=FAIL

Finally block failing
    FAIL    PASS    FAIL
