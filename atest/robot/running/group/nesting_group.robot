*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/group/nesting_group.robot
Resource          atest_resource.robot

*** Test Cases ***
Test with Nested Groups
    ${tc}    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc}[0]         type=GROUP      name=
    Check Body Item Data    ${tc}[0, 0]       type=KEYWORD    name=Set Variable
    Check Body Item Data    ${tc}[0, 1]       type=GROUP      name=This Is A Named Group
    Check Body Item Data    ${tc}[0, 1, 0]     type=KEYWORD    name=Should Be Equal

Group with other control structure
    Check Test Case    ${TESTNAME}

Test With Not Executed Groups
    Check Test Case    ${TESTNAME}
