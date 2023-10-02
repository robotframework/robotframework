*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/telnet/connections.robot
Resource          telnet_resource.robot

*** Test Cases ***
Open Connection
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    Opening connection to localhost:23 with prompt: xxx

Close Connection
    ${tc} =    Check Test Case    ${TEST NAME}
    Check Log Message    ${tc.kws[1].msgs[0]}    *hello    pattern=yes

Closing already closed connection is OK
    Check Test Case    ${TEST NAME}

Close All Connections
    Check Test Case    ${TEST NAME} 1
    Check Test Case    ${TEST NAME} 2

Switch Connection
    Check Test Case    ${TEST NAME}
