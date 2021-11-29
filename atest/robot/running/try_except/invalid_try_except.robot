*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/invalid_try_except.robot
Test Template     Verify try except and block statuses

*** Test Cases ***
Try without END
    FAIL    NOT RUN

Try without except or finally
    FAIL

Try with argument
    FAIL    NOT RUN

Try else with argument
    FAIL    NOT RUN    NOT RUN

Finally with argument
    FAIL    NOT RUN    NOT RUN
