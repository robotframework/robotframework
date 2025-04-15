*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/group/templates.robot
Resource          atest_resource.robot

*** Test Cases ***
Pass
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}       type=GROUP      status=PASS    children=1    name=1
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD    status=PASS    children=1    name=Run Keyword    args=Log, 1.1
    Check Body Item Data    ${tc[1]}       type=GROUP      status=PASS    children=2    name=2
    Check Body Item Data    ${tc[1, 0]}    type=KEYWORD    status=PASS    children=1    name=Run Keyword    args=Log, 2.1
    Check Body Item Data    ${tc[1, 1]}    type=KEYWORD    status=PASS    children=1    name=Run Keyword    args=Log, 2.2

Pass and fail
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}       type=GROUP      status=PASS    children=1    name=1
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD    status=PASS    children=1    name=Run Keyword    args=Log, 1.1
    Check Body Item Data    ${tc[1]}       type=GROUP      status=FAIL    children=2    name=2                                message=2.1
    Check Body Item Data    ${tc[1, 0]}    type=KEYWORD    status=FAIL    children=1    name=Run Keyword    args=Fail, 2.1    message=2.1
    Check Body Item Data    ${tc[1, 1]}    type=KEYWORD    status=PASS    children=1    name=Run Keyword    args=Log, 2.2
    Check Body Item Data    ${tc[2]}       type=GROUP      status=PASS    children=1    name=3
    Check Body Item Data    ${tc[2, 0]}    type=KEYWORD    status=PASS    children=1    name=Run Keyword    args=Log, 3.1

Fail multiple times
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}       type=GROUP      status=FAIL    children=1    name=1                                message=1.1
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD    status=FAIL    children=1    name=Run Keyword    args=Fail, 1.1    message=1.1
    Check Body Item Data    ${tc[1]}       type=GROUP      status=FAIL    children=3    name=2                                message=Several failures occurred:\n\n1) 2.1\n\n2) 2.3
    Check Body Item Data    ${tc[1, 0]}    type=KEYWORD    status=FAIL    children=1    name=Run Keyword    args=Fail, 2.1    message=2.1
    Check Body Item Data    ${tc[1, 1]}    type=KEYWORD    status=PASS    children=1    name=Run Keyword    args=Log, 2.2
    Check Body Item Data    ${tc[1, 2]}    type=KEYWORD    status=FAIL    children=1    name=Run Keyword    args=Fail, 2.3    message=2.3
    Check Body Item Data    ${tc[2]}       type=GROUP      status=PASS    children=1    name=3
    Check Body Item Data    ${tc[2, 0]}    type=KEYWORD    status=PASS    children=1    name=Run Keyword    args=Log, 3.1
    Check Body Item Data    ${tc[3]}       type=GROUP      status=FAIL    children=1    name=4                                message=4.1
    Check Body Item Data    ${tc[3, 0]}    type=KEYWORD    status=FAIL    children=1    name=Run Keyword    args=Fail, 4.1    message=4.1

Pass and skip
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}       type=GROUP      status=SKIP    children=1    name=1                                message=1.1
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD    status=SKIP    children=1    name=Run Keyword    args=Skip, 1.1    message=1.1
    Check Body Item Data    ${tc[1]}       type=GROUP      status=PASS    children=1    name=2
    Check Body Item Data    ${tc[1, 0]}    type=KEYWORD    status=PASS    children=1    name=Run Keyword    args=Log, 2.1
    Check Body Item Data    ${tc[2]}       type=GROUP      status=PASS    children=2    name=3
    Check Body Item Data    ${tc[2, 0]}    type=KEYWORD    status=SKIP    children=1    name=Run Keyword    args=Skip, 3.1    message=3.1
    Check Body Item Data    ${tc[2, 1]}    type=KEYWORD    status=PASS    children=1    name=Run Keyword    args=Log, 3.2

Pass, fail and skip
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}       type=GROUP      status=FAIL    children=3    name=1                                message=1.1
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD    status=FAIL    children=1    name=Run Keyword    args=Fail, 1.1    message=1.1
    Check Body Item Data    ${tc[0, 1]}    type=KEYWORD    status=SKIP    children=1    name=Run Keyword    args=Skip, 1.2    message=1.2
    Check Body Item Data    ${tc[0, 2]}    type=KEYWORD    status=PASS    children=1    name=Run Keyword    args=Log, 1.3
    Check Body Item Data    ${tc[1]}       type=GROUP      status=SKIP    children=1    name=2                                message=2.1
    Check Body Item Data    ${tc[1, 0]}    type=KEYWORD    status=SKIP    children=1    name=Run Keyword    args=Skip, 2.1    message=2.1
    Check Body Item Data    ${tc[2]}       type=GROUP      status=PASS    children=1    name=3
    Check Body Item Data    ${tc[2, 0]}    type=KEYWORD    status=PASS    children=1    name=Run Keyword    args=Log, 3.1

Skip all
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}       type=GROUP      status=SKIP    children=2    name=1                                message=All iterations skipped.
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD    status=SKIP    children=1    name=Run Keyword    args=Skip, 1.1    message=1.1
    Check Body Item Data    ${tc[0, 1]}    type=KEYWORD    status=SKIP    children=1    name=Run Keyword    args=Skip, 1.2    message=1.2
    Check Body Item Data    ${tc[1]}       type=GROUP      status=SKIP    children=1    name=2                                message=2.1
    Check Body Item Data    ${tc[1, 0]}    type=KEYWORD    status=SKIP    children=1    name=Run Keyword    args=Skip, 2.1    message=2.1

Just one that is skipped
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}       type=GROUP      status=SKIP    children=1    name=1                                message=1.1
    Check Body Item Data    ${tc[0, 0]}    type=KEYWORD    status=SKIP    children=1    name=Run Keyword    args=Skip, 1.1    message=1.1
