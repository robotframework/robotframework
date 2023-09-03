*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/async_keywords.robot
Resource         atest_resource.robot

*** Test Cases ***
Works With Asyncio Run
    [Tags]    require-py3.7
    Check Test Case    ${TESTNAME}

Basic Async Works
    Check Test Case    ${TESTNAME}

Works Using Gather
    Check Test Case    ${TESTNAME}

Long Async Tasks Run In Background
    [Tags]    require-py3.7
    Check Test Case    ${TESTNAME}

Builtin Call From Library Works
    Check Test Case    ${TESTNAME}

Create Task With Loop Reference
    Check Test Case    ${TESTNAME}

Generators Do Not Use Event Loop
    Check Test Case    ${TESTNAME}
