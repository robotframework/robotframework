*** Settings ***
Suite Setup               Run Tests With Keyword Running Listener
Resource                  listener_resource.robot

*** Test Cases ***
In start_suite when suite has no setup
    Should Be Equal       ${SUITE.setup.name}                      Implicit setup
    Should Be Equal       ${SUITE.setup.body[0].name}              BuiltIn.Log
    Check Log Message     ${SUITE.setup.body[0].body[0]}           start_suite
    Length Should Be      ${SUITE.setup.body}                      1

In end_suite when suite has no teardown
    Should Be Equal       ${SUITE.teardown.name}                   Implicit teardown
    Should Be Equal       ${SUITE.teardown.body[0].name}           BuiltIn.Log
    Check Log Message     ${SUITE.teardown.body[0].body[0]}        end_suite
    Length Should Be      ${SUITE.teardown.body}                   1

In start_suite when suite has setup
    ${suite} =            Set Variable                             ${SUITE.suites[1]}
    Should Be Equal       ${suite.setup.name}                      Suite Setup
    Should Be Equal       ${suite.setup.body[0].name}              BuiltIn.Log
    Check Log Message     ${suite.setup.body[0].body[0]}           start_suite
    Length Should Be      ${suite.setup.body}                      5

In end_suite when suite has teardown
    ${suite} =            Set Variable                             ${SUITE.suites[1]}
    Should Be Equal       ${suite.teardown.name}                   Suite Teardown
    Should Be Equal       ${suite.teardown.body[-1].name}          BuiltIn.Log
    Check Log Message     ${suite.teardown.body[-1].body[0]}       end_suite
    Length Should Be      ${suite.teardown.body}                   5

In start_test and end_test when test has no setup or teardown
    ${tc} =               Check Test Case                          First One
    Should Be Equal       ${tc.body[0].name}                       BuiltIn.Log
    Check Log Message     ${tc.body[0].body[0]}                    start_test
    Should Be Equal       ${tc.body[-1].name}                      BuiltIn.Log
    Check Log Message     ${tc.body[-1].body[0]}                   end_test
    Length Should Be      ${tc.body}                               5
    Should Not Be True    ${tc.setup}
    Should Not Be True    ${tc.teardown}

In start_test and end_test when test has setup and teardown
    ${tc} =               Check Test Case                          Test with setup and teardown
    Should Be Equal       ${tc.body[0].name}                       BuiltIn.Log
    Check Log Message     ${tc.body[0].body[0]}                    start_test
    Should Be Equal       ${tc.body[-1].name}                      BuiltIn.Log
    Check Log Message     ${tc.body[-1].body[0]}                   end_test
    Length Should Be      ${tc.body}                               3
    Should Be Equal       ${tc.setup.name}                         Test Setup
    Should Be Equal       ${tc.teardown.name}                      Test Teardown

In start_keyword and end_keyword with library keyword
    ${tc} =               Check Test Case                          First One
    Should Be Equal       ${tc.body[1].name}                       BuiltIn.Log
    Should Be Equal       ${tc.body[1].body[0].name}               BuiltIn.Log
    Check Log Message     ${tc.body[1].body[0].body[0]}            start_keyword
    Check Log Message     ${tc.body[1].body[1]}                    Test 1
    Should Be Equal       ${tc.body[1].body[2].name}               BuiltIn.Log
    Check Log Message     ${tc.body[1].body[2].body[0]}            end_keyword
    Length Should Be      ${tc.body[1].body}                       3

In start_keyword and end_keyword with user keyword
    ${tc} =               Check Test Case                          First One
    Should Be Equal       ${tc.body[3].name}                       logs on trace
    Should Be Equal       ${tc.body[3].body[0].name}               BuiltIn.Log
    Check Log Message     ${tc.body[3].body[0].body[0]}            start_keyword
    Should Be Equal       ${tc.body[3].body[1].name}               BuiltIn.Log
    Should Be Equal       ${tc.body[3].body[1].body[0].name}       BuiltIn.Log
    Check Log Message     ${tc.body[3].body[1].body[0].body[0]}    start_keyword
    Should Be Equal       ${tc.body[3].body[1].body[1].name}       BuiltIn.Log
    Check Log Message     ${tc.body[3].body[1].body[1].body[0]}    end_keyword
    Length Should Be      ${tc.body[3].body[1].body}               2
    Should Be Equal       ${tc.body[3].body[2].name}               BuiltIn.Log
    Check Log Message     ${tc.body[3].body[2].body[0]}            end_keyword
    Length Should Be      ${tc.body[3].body}                       3

*** Keywords ***
Run Tests With Keyword Running Listener
    ${path} =    Normalize Path    ${LISTENER DIR}/keyword_running_listener.py
    Run Tests    --listener ${path}    misc/normal.robot misc/setups_and_teardowns.robot
    Should Be Empty    ${ERRORS}
