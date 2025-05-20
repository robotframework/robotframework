*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/group/invalid_group.robot
Resource          atest_resource.robot

*** Test Cases ***
END missing
    ${tc} =    Check Test Case    ${TESTNAME}
    Length Should Be        ${tc.body}    1
    Check Body Item Data    ${tc[0]}      GROUP      status=FAIL       children=2    message=GROUP must have closing END.
    Check Body Item Data    ${tc[0, 0]}   KEYWORD    status=NOT RUN    children=0    name=Fail    args=Not run
    Check Body Item Data    ${tc[0, 1]}   MESSAGE    level=FAIL                      message=GROUP must have closing END.

Empty
    ${tc}    Check Test Case    ${TESTNAME}
    Length Should Be        ${tc.body}    2
    Check Body Item Data    ${tc[0]}      GROUP      status=FAIL       children=1    message=GROUP cannot be empty.
    Check Body Item Data    ${tc[0, 0]}   MESSAGE    level=FAIL                      message=GROUP cannot be empty.
    Check Body Item Data    ${tc[1]}      KEYWORD    status=NOT RUN    children=0    name=Log    args=Outside

Multiple parameters
    ${tc}    Check Test Case    ${TESTNAME}
    Length Should Be        ${tc.body}    2
    Check Body Item Data    ${tc[0]}      GROUP      status=FAIL       children=2    message=GROUP accepts only one argument as name, got 3 arguments 'Too', 'many' and 'values'.
    Check Body Item Data    ${tc[0, 0]}   KEYWORD    status=NOT RUN    children=0    name=Fail    args=Not run
    Check Body Item Data    ${tc[0, 1]}   MESSAGE    level=FAIL                      message=GROUP accepts only one argument as name, got 3 arguments 'Too', 'many' and 'values'.
    Check Body Item Data    ${tc[1]}      KEYWORD    status=NOT RUN    children=0    name=Log    args=Last Keyword

Non-existing variable in name
    ${tc}    Check Test Case    ${TESTNAME}
    Length Should Be        ${tc.body}    2
    Check Body Item Data    ${tc[0]}      GROUP      status=FAIL       children=2    message=Variable '\${non_existing_var}' not found.    name=\${non_existing_var} in name
    Check Body Item Data    ${tc[0, 0]}   KEYWORD    status=NOT RUN    children=0    name=Fail    args=Not run
    Check Body Item Data    ${tc[0, 1]}   MESSAGE    level=FAIL                      message=Variable '\${non_existing_var}' not found.
    Check Body Item Data    ${tc[1]}      KEYWORD    status=NOT RUN    children=0    name=Log    args=Last Keyword

Invalid data is not reported after failures
    ${tc}    Check Test Case    ${TESTNAME}
    Length Should Be        ${tc.body}    4
    Check Body Item Data    ${tc[0]}      KEYWORD    status=FAIL       children=1    name=Fail    args=Something bad happened!    message=Something bad happened!
    Check Body Item Data    ${tc[1]}      GROUP      status=NOT RUN    children=1    name=\${non_existing_non_executed_variable_is_ok}
    Check Body Item Data    ${tc[1, 0]}   KEYWORD    status=NOT RUN    children=0    name=Fail    args=Not run
    Check Body Item Data    ${tc[2]}      GROUP      status=NOT RUN    children=0    name=Empty non-executed GROUP is ok
    Check Body Item Data    ${tc[3]}      GROUP      status=NOT RUN    children=1    name=Even missing END is ok
    Check Body Item Data    ${tc[3, 0]}   KEYWORD    status=NOT RUN    children=0    name=Fail    args=Not run
