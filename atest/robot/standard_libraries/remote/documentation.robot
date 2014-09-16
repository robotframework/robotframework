*** Settings ***
Suite Setup      Run Remote Tests    documentation.robot    documentation.py
Force Tags       regression    pybot    jybot
Resource         remote_resource.robot

*** Test Cases ***
Empty
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].doc}    ${EMPTY}

Single line
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].doc}    Single line documentation

Multi line
    ${tc} =    Check Test Case    ${TEST NAME}
    Should Be Equal    ${tc.kws[0].doc}    Multi
