*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/try_except_in_uk.robot
Test Template     Verify try except and block statuses in uk

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

Finally block executed when no failures
    PASS    NOT RUN    PASS    PASS

Finally block executed after catch
    FAIL    PASS    PASS

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

Return in try
    PASS    NOT RUN    NOT RUN    PASS

Return in except handler
    FAIL    PASS    NOT RUN    PASS

Return in else
    PASS    NOT RUN    PASS    PASS

*** Keywords ***
Verify try except and block statuses in uk
    [Arguments]    @{types_and_statuses}    ${tc_status}=    ${path}=body[0].body[0]
    Verify try except and block statuses    @{types_and_statuses}    tc_status=${tc_status}    path=${path}
