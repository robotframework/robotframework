*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/group/group.robot
Resource          atest_resource.robot

*** Test Cases ***
Simple GROUP
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}      type=GROUP        name=name 1    children=2
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD      name=Log       args=low level
    Check Body Item Data    ${tc[1]}      type=GROUP        name=name 2    children=1
    Check Body Item Data    ${tc[1, 0]}    type=KEYWORD      name=Log
    Check Body Item Data    ${tc[2]}      type=KEYWORD      name=Log       args=this is the end

GROUP in keywords
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}      type=KEYWORD      name=Keyword With A Group     children=4
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD      name=Log                      args=top level
    Check Body Item Data    ${tc[0, 1]}    type=GROUP        name=frist keyword GROUP      children=2
    Check Body Item Data    ${tc[0, 2]}    type=GROUP        name=second keyword GROUP     children=1
    Check Body Item Data    ${tc[0, 3]}    type=KEYWORD      name=Log                      args=this is the end

Anonymous GROUP
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}      type=GROUP        name=${EMPTY}    children=1
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD      name=Log       args=this group has no name

Test With Vars In GROUP Name
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}      type=GROUP        name=Test is named: Test With Vars In GROUP Name    children=1
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD      name=Log       args=\${TEST_NAME}
    Check Log Message       ${tc[0, 0, 0]}    Test With Vars In GROUP Name
    Check Body Item Data    ${tc[1]}      type=GROUP        name=42    children=1
    Check Body Item Data    ${tc[1, 0]}    type=KEYWORD      name=Log       args=Should be 42

