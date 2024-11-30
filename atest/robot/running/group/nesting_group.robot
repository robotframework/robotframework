*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    running/group/nesting_group.robot
Resource          atest_resource.robot

*** Test Cases ***
Test with Nested Groups
    ${tc}    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}           type=GROUP      name=
    Check Body Item Data    ${tc[0, 0]}        type=KEYWORD    name=Set Variable
    Check Body Item Data    ${tc[0, 1]}        type=GROUP      name=This Is A Named Group
    Check Body Item Data    ${tc[0, 1, 0]}     type=KEYWORD    name=Should Be Equal

Group with other control structure
    ${tc}    Check Test Case    ${TESTNAME}
    Check Body Item Data    ${tc[0]}                         type=IF/ELSE ROOT
    Check Body Item Data    ${tc[0, 0]}                      type=IF                condition=True                         children=2
    Check Body Item Data    ${tc[0, 0, 0]}                   type=GROUP             name=Hello                             children=1
    Check Body Item Data    ${tc[0, 0, 0, 0]}                type=VAR               name=\${i}
    Check Body Item Data    ${tc[0, 0, 1]}                   type=GROUP             name=With WHILE                        children=2
    Check Body Item Data    ${tc[0, 0, 1, 0]}                type=WHILE             condition=$i < 2                       children=2
    Check Body Item Data    ${tc[0, 0, 1, 0, 0]}             type=ITERATION
    Check Body Item Data    ${tc[0, 0, 1, 0, 0, 0]}          type=GROUP             name=Group1 Inside WHILE               children=1
    Check Body Item Data    ${tc[0, 0, 1, 0, 0, 0, 0]}       type=KEYWORD           name=Log           args=\${i}
    Check Body Item Data    ${tc[0, 0, 1, 0, 0, 1]}          type=GROUP             name=Group2 Inside WHILE               children=1
    Check Body Item Data    ${tc[0, 0, 1, 0, 0, 1, 0]}       type=VAR               name=\${i}         value=\${i + 1}
    Check Body Item Data    ${tc[0, 0, 1, 0, 1]}             type=ITERATION
    Check Body Item Data    ${tc[0, 0, 1, 0, 1, 0]}          type=GROUP             name=Group1 Inside WHILE               children=1
    Check Body Item Data    ${tc[0, 0, 1, 0, 1, 0, 0]}       type=KEYWORD           name=Log           args=\${i}
    Check Body Item Data    ${tc[0, 0, 1, 0, 1, 1]}          type=GROUP             name=Group2 Inside WHILE               children=1
    Check Body Item Data    ${tc[0, 0, 1, 0, 1, 1, 0]}       type=VAR               name=\${i}         value=\${i + 1}
    Check Body Item Data    ${tc[0, 0, 1, 1]}                type=IF/ELSE ROOT
    Check Body Item Data    ${tc[0, 0, 1, 1, 0]}             type=IF                status=NOT RUN     condition=$i != 2    children=1
    Check Body Item Data    ${tc[0, 0, 1, 1, 0, 0]}          type=KEYWORD           status=NOT RUN     name=Fail            args=Shall be logged but NOT RUN



Test With Not Executed Groups
    ${tc}    Check Test Case    ${TESTNAME}    status=FAIL    message=GROUP in ELSE is not executed.
