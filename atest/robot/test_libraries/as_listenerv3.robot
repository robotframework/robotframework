*** Settings ***
Suite Setup     Run Tests    ${EMPTY}    test_libraries/as_listener/listener_library3.robot
Resource        atest_resource.robot

*** Test Cases ***
New tests and keywords can be added to suite
   ${tc} =    Check test case    New   FAIL    Message: [start] [end]
   Stdout Should Contain    SEPARATOR=\n
   ...    New ${SPACE*65} | FAIL |
   ...    Message: [start] [end]
   Check keyword data    ${tc.kws[0]}    BuiltIn.No Operation

Test status and message can be changed
    Check Test case    Pass    FAIL    Message: [start] [end]
    Check Test case    Fail    PASS    Failing [end]
    Stdout Should Contain    SEPARATOR=\n
    ...    Pass ${SPACE*64} | FAIL |
    ...    Message: [start] [end]
    Stdout Should Contain    SEPARATOR=\n
    ...    Fail ${SPACE*64} | PASS |
    ...    Failing [end]

Test tags can be modified
   Check Test Tags    Fail    [end]  [start]

Metadata can be modified
   Should be equal    ${SUITE.metadata['suite']}   [start] [end]
   Should be equal    ${SUITE.metadata['tests']}   xxx

Log messages and timestamps can be changed
   ${tc}=   Get test case    Pass
   Check log message    ${tc.kws[0].msgs[0]}    Passing [log_message]
   Should be equal    ${tc.kws[0].msgs[0].timestamp}    ${datetime(2015, 12, 16, 15, 51,20, 141000)}

Message to syslog can be changed
   Syslog Should Contain    2015-12-16 15:51:20.141000 | WARN \ | Foo [log_message] [message]
   Check log message    ${ERRORS[0]}    Foo [log_message] [message]    WARN

Close is called
   ${close} =    Set variable    CLOSING Listener library 3\n
   Stderr Should Contain    ${close*4}
