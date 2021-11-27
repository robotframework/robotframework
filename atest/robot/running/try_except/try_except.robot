*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/try_except.robot
Test Template     Block statuses should be

*** Test Cases ***
Try with no failures
    PASS    NOT RUN

First except executed
    FAIL    PASS

Second except executed
    FAIL    NOT RUN    PASS    NOT RUN

Except handler failing
    FAIL    FAIL

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
    PASS    NOT RUN    PASS

Finally block executed after catch
    FAIL    PASS    PASS

Finally block failing
    FAIL    PASS    FAIL
