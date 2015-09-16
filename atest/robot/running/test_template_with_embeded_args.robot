*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    running/test_template_with_embeded_args.robot
Resource         atest_resource.robot

*** Test Cases ***
Matching arguments
    ${tc} =    Check Test Case    ${TESTNAME}
    Keyword should be    ${tc.kws[0]}   The result of 1 + 1 should be 2
    Keyword should be    ${tc.kws[1]}   The result of 1 + 2 should be 3
    Keyword should be    ${tc.kws[2]}   The result of 1 + 3 should be 5

Argument names do not need to be same as in definition
    ${tc} =    Check Test Case    ${TESTNAME}
    Keyword should be    ${tc.kws[0]}   The result of 1 + 1 should be 2
    Keyword should be    ${tc.kws[1]}   The result of 1 + 2 should be 3
    Keyword should be    ${tc.kws[2]}   The result of 1 + 3 should be 5

Some arguments can be hard-coded
    ${tc} =    Check Test Case    ${TESTNAME}
    Keyword should be    ${tc.kws[0]}   The result of 1 + 1 should be 3
    Keyword should be    ${tc.kws[1]}   The result of 1 + 2 should be 3
    Keyword should be    ${tc.kws[2]}   The result of 1 + 3 should be 3

Can have different arguments than definition
    ${tc} =    Check Test Case    ${TESTNAME}
    Keyword should be    ${tc.kws[0]}   The result of 38 + 3 + 1 should be 42
    Keyword should be    ${tc.kws[1]}   The non-existing of 666 should be 42

Can use variables
    ${tc} =    Check Test Case    ${TESTNAME}
    Keyword should be    ${tc.kws[0]}   The result of \${1} + \${2} should be \${3}

Cannot have more arguments than variables
    ${tc} =    Check Test Case    ${TESTNAME}
    Keyword should be    ${tc.kws[0]}    The result of \${calc} should be 3
    ...    1 + 2    extra

Cannot have less arguments than variables
    ${tc} =    Check Test Case    ${TESTNAME}
    Keyword should be    ${tc.kws[0]}    The result of \${calc} should be \${extra}
    ...    1 + 2

*** Keywords ***
Keyword should be
    [Arguments]    ${kw}    ${name}    @{args}
    Should Be Equal    ${kw.name}    ${name}
    Lists Should Be Equal    ${kw.args}    ${args}
