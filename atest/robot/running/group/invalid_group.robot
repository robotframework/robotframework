*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/group/invalid_group.robot
Resource          atest_resource.robot

*** Test Cases ***
END missing
    ${tc}    Check Test Case    ${TESTNAME}    status=FAIL    message=GROUP must have closing END.
    Length Should Be    ${tc.body}    1
    Check Body Item Data    ${tc[0]}    GROUP    status=FAIL    children=1    message=GROUP must have closing END.

Empty GROUP
    ${tc}    Check Test Case    ${TESTNAME}        status=FAIL                     message=GROUP cannot be empty.
    Length Should Be    ${tc.body}    2
    Check Body Item Data    ${tc[0]}    GROUP      status=FAIL       children=1    message=GROUP cannot be empty.
    Check Body Item Data    ${tc[1]}    KEYWORD    status=NOT RUN                  name=Log    args=Last Keyword

Multiple Parameters
    ${tc}    Check Test Case    ${TESTNAME}    status=FAIL    message=GROUP accepts only one argument as name, got 3 arguments 'Log', '123' and '321'.
    Length Should Be    ${tc.body}    2
    Check Body Item Data    ${tc[0]}    GROUP      status=FAIL       children=1    message=GROUP accepts only one argument as name, got 3 arguments 'Log', '123' and '321'.
    Check Body Item Data    ${tc[1]}    KEYWORD    status=NOT RUN                  name=Log    args=Last Keyword

Non existing var in Name
    ${tc}    Check Test Case    ${TESTNAME}    status=FAIL    message=Variable '\${non_existing_var}' not found.
    Length Should Be    ${tc.body}    2
    Check Body Item Data    ${tc[0]}    GROUP      status=FAIL       children=1    message=Variable '\${non_existing_var}' not found.
    Check Body Item Data    ${tc[1]}    KEYWORD    status=NOT RUN                  name=Log    args=Last Keyword
