*** Settings ***
Suite Setup     Run Tests  ${EMPTY}  standard_libraries/builtin/misc.txt
Force Tags      regression  jybot  pybot
Resource        atest_resource.txt

*** Test Cases ***
No Operation
    Check Test Case  ${TEST NAME}

Catenate
    Check Test Case  ${TEST NAME}

Comment
    ${tc} =  Check Test Case  ${TEST NAME}
    Should Be Empty  ${tc.kws[0].msgs}
    Should Be Empty  ${tc.kws[1].msgs}
    Should Be Empty  ${tc.kws[2].msgs}

Regexp Escape
    Check Test Case  ${TEST NAME}
