*** Settings ***
Suite Setup       Run Tests    --listener ${LISTENER DIR}/modify_timeouts.py    output/listener_interface/modify_timeouts.robot
Resource          listener_resource.robot

*** Test Cases ***
Test timeouts can be added and shortened
    ${tc} =    Check Test Case    Add test timeout
    Should Be Equal    ${tc.timeout}    100 milliseconds
    ${tc} =    Check Test Case    Shorten test timeout
    Should Be Equal    ${tc.timeout}    100 milliseconds

Test timeouts can be extended
    ${tc} =    Check Test Case    Extend test timeout
    Should Be Equal    ${tc.timeout}    1 minute

Test timeouts can be removed
    ${tc} =    Check Test Case    Remove test timeout
    Should Be Equal    ${tc.timeout}    ${None}
    ${tc} =    Check Test Case    Disable test timeout
    Should Be Equal    ${tc.timeout}    ${None}

Timeouts can use variables set by listeners
    ${tc} =    Check Test Case    Timeout from listener variable
    Should Be Equal    ${tc.timeout}    100 milliseconds

Invalid timeouts fail normally
    Check Test Case    Invalid timeout from listener

Modified timeouts apply to setup
    Check Test Case    Timeout in setup

Unchanged timeouts still apply
    Check Test Case    Unchanged timeout

Keyword timeouts can be changed
    ${tc} =    Check Test Case    Keyword timeouts can be changed
    Should Be Equal    ${tc[0].timeout}    100 milliseconds

Keyword timeouts can be removed
    ${tc} =    Check Test Case    Keyword timeouts can be removed
    Should Be Equal    ${tc[0].timeout}    ${None}
