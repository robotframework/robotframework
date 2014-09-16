*** Settings ***
Suite Setup      Run Remote Tests    simple_server.robot    simpleserver.py
Force Tags       regression    pybot    jybot
Resource         remote_resource.robot

*** Test Cases ***
Passing
    Check Test Case    ${TESTNAME}

Failing
    Check Test Case    ${TESTNAME}

Failing with traceback
    Check Test Case    ${TESTNAME}

Returning
    Check Test Case    ${TESTNAME}

Logging
    ${tc} =    Check Test Case    ${TESTNAME}
    Check Log Message    ${tc.kws[0].msgs[0]}    I can has logz?
    Check Log Message    ${tc.kws[0].msgs[1]}    Yezz!!    DEBUG

Extra stuff in result dictionary is ignored
    Check Test Case    ${TESTNAME}

Keyword documentation
    [Documentation]    Library does not have `get_keyword_documentation` method.
    ${tc} =    Get Test Case    Passing
    Should Be Equal    ${tc.kws[0].doc}    ${EMPTY}
