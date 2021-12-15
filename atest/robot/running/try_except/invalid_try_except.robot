*** Settings ***
Resource          try_except_resource.robot
Suite Setup       Run Tests    ${EMPTY}    running/try_except/invalid_try_except.robot
Test Template     Verify try except and block statuses

*** Test Cases ***
Try without END
    FAIL    NOT RUN    NOT RUN

Try without body
    FAIL    NOT RUN    NOT RUN

Try without except or finally
    FAIL

Try with argument
    FAIL    NOT RUN    NOT RUN

Except without body
    FAIL    NOT RUN    NOT RUN    NOT RUN

Default except not last
    FAIL    NOT RUN    NOT RUN    NOT RUN

Multiple default excepts
    FAIL    NOT RUN    NOT RUN    NOT RUN

AS not the second last token
    FAIL    NOT RUN

Invalid AS variable
    FAIL    NOT RUN

Else with argument
    FAIL    NOT RUN    NOT RUN    NOT RUN

Else without body
    FAIL    NOT RUN    NOT RUN

Multiple else blocks
    FAIL    NOT RUN    NOT RUN    NOT RUN

Finally with argument
    FAIL    NOT RUN    NOT RUN

Finally without body
    FAIL    NOT RUN

Multiple finally blocks
    FAIL    NOT RUN    NOT RUN

Else before except
    FAIL    NOT RUN    NOT RUN    NOT RUN   NOT RUN

Finally before except
    FAIL    NOT RUN    NOT RUN    NOT RUN

Finally before else
    FAIL    NOT RUN    NOT RUN    NOT RUN
