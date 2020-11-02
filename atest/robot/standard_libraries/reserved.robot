*** Settings ***
Suite Setup       Run Tests    ${EMPTY}    standard_libraries/reserved.robot
Resource          atest_resource.robot

*** Test Cases ***
Markers should get note about case
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

Others should just be reserved
    Check Test Case    ${TESTNAME} 1
    Check Test Case    ${TESTNAME} 2

'End' gets extra note
    Check Test Case    ${TESTNAME}

'Else' gets extra note
    Check Test Case    ${TESTNAME}

'Else if' gets extra note
    Check Test Case    ${TESTNAME}

'Elif' gets extra note
    Check Test Case    ${TESTNAME}

Reserved in user keyword
    Check Test Case    ${TESTNAME}
