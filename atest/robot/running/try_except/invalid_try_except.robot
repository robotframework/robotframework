*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/invalid_try_except.robot
Test Template     Block statuses should be

*** Test Cases ***
Try without END
    FAIL    NOT RUN

Try with argument
    FAIL    NOT RUN
