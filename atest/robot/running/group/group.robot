*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/group/group.robot
Resource          atest_resource.robot

*** Test Cases ***
Basics
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}       type=GROUP        name=1st group    children=2
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD      name=Log          args=Inside group
    Check Body Item Data    ${tc[0, 1]}    type=KEYWORD      name=Log          args=Still inside
    Check Body Item Data    ${tc[1]}       type=GROUP        name=second       children=1
    Check Body Item Data    ${tc[1, 0]}    type=KEYWORD      name=Log          args=Inside second group
    Check Body Item Data    ${tc[2]}       type=KEYWORD      name=Log          args=After

Failing
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}       type=GROUP        name=Fails        children=2    status=FAIL    message=Failing inside GROUP!
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD      name=Fail         children=1    status=FAIL    message=Failing inside GROUP!
    Check Body Item Data    ${tc[0, 1]}    type=KEYWORD      name=Fail         children=0    status=NOT RUN
    Check Body Item Data    ${tc[1]}       type=GROUP        name=Not run      children=1    status=NOT RUN
    Check Body Item Data    ${tc[1, 0]}    type=KEYWORD      name=Fail         children=0    status=NOT RUN

Anonymous
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}       type=GROUP        name=${EMPTY}     children=1
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD      name=Log          args=Inside unnamed group

Variable in name
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}       type=GROUP        name=Test is named: ${TEST NAME}    children=1
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD      name=Log          args=\${TEST_NAME}
    Check Log Message       ${tc[0, 0, 0]}    ${TEST NAME}
    Check Body Item Data    ${tc[1]}       type=GROUP        name=42           children=1
    Check Body Item Data    ${tc[1, 0]}    type=KEYWORD      name=Log          args=Should be 42

In user keyword
    ${tc}=    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}       type=KEYWORD      name=Keyword      children=4
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD      name=Log          args=Before
    Check Body Item Data    ${tc[0, 1]}    type=GROUP        name=First        children=2
    Check Body Item Data    ${tc[0, 2]}    type=GROUP        name=Second       children=1
    Check Body Item Data    ${tc[0, 3]}    type=KEYWORD      name=Log          args=After
