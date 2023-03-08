*** Settings ***
Suite Setup      Run Tests    ${EMPTY}    keywords/async_keywords.robot
Resource         atest_resource.robot

*** Test Cases ***
Works With Asyncio Run
    Check Test Case    ${TESTNAME}

Basic Async Works
    Check Test Case    ${TESTNAME}

Works Using Gather
    Check Test Case    ${TESTNAME}

Builtin Async Sleep Keyword Works
    Check Test Case    ${TESTNAME}

Long Async Tasks Run In Background
    Check Test Case    ${TESTNAME}

Builtin Call From Library Works
    Check Test Case    ${TESTNAME}

Builtin Gather Keyword Works
    Check Test Case    ${TESTNAME}

Builtin Gather Keyword Fails If Keyword Is Not Async
    Check Test Case    ${TEST NAME}    status=FAIL    message=Keyword 'No Operation' is not async
