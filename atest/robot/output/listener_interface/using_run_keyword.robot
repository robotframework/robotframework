*** Settings ***
Suite Setup               Run Tests With Keyword Running Listener
Resource                  listener_resource.robot

*** Test Cases ***
In start_suite when suite has no setup
    Should Be Equal       ${SUITE.setup.full_name}                 Implicit setup
    Should Be Equal       ${SUITE.setup.body[0].full_name}         BuiltIn.Log
    Check Log Message     ${SUITE.setup.body[0].body[0]}           start_suite
    Length Should Be      ${SUITE.setup.body}                      1

In end_suite when suite has no teardown
    Should Be Equal       ${SUITE.teardown.full_name}              Implicit teardown
    Should Be Equal       ${SUITE.teardown.body[0].full_name}      BuiltIn.Log
    Check Log Message     ${SUITE.teardown.body[0].body[0]}        end_suite
    Length Should Be      ${SUITE.teardown.body}                   1

In start_suite when suite has setup
    ${suite} =            Set Variable                             ${SUITE.suites[1]}
    Should Be Equal       ${suite.setup.full_name}                 Suite Setup
    Should Be Equal       ${suite.setup.body[0].full_name}         BuiltIn.Log
    Check Log Message     ${suite.setup.body[0].body[0]}           start_suite
    Length Should Be      ${suite.setup.body}                      5

In end_suite when suite has teardown
    ${suite} =            Set Variable                             ${SUITE.suites[1]}
    Should Be Equal       ${suite.teardown.full_name}              Suite Teardown
    Should Be Equal       ${suite.teardown.body[-1].full_name}     BuiltIn.Log
    Check Log Message     ${suite.teardown.body[-1].body[0]}       end_suite
    Length Should Be      ${suite.teardown.body}                   5

In start_test and end_test when test has no setup or teardown
    ${tc} =               Check Test Case                          First One
    Should Be Equal       ${tc.body[0].full_name}                  BuiltIn.Log
    Check Log Message     ${tc.body[0].body[0]}                    start_test
    Should Be Equal       ${tc.body[-1].full_name}                 BuiltIn.Log
    Check Log Message     ${tc.body[-1].body[0]}                   end_test
    Length Should Be      ${tc.body}                               5
    Should Not Be True    ${tc.setup}
    Should Not Be True    ${tc.teardown}

In start_test and end_test when test has setup and teardown
    ${tc} =               Check Test Case                          Test with setup and teardown
    Should Be Equal       ${tc.body[0].full_name}                  BuiltIn.Log
    Check Log Message     ${tc.body[0].body[0]}                    start_test
    Should Be Equal       ${tc.body[-1].full_name}                 BuiltIn.Log
    Check Log Message     ${tc.body[-1].body[0]}                   end_test
    Length Should Be      ${tc.body}                               3
    Should Be Equal       ${tc.setup.full_name}                    Test Setup
    Should Be Equal       ${tc.teardown.full_name}                 Test Teardown

In start_keyword and end_keyword with library keyword
    ${tc} =               Check Test Case                          First One
    Should Be Equal       ${tc.body[1].full_name}                  BuiltIn.Log
    Should Be Equal       ${tc.body[1].body[0].full_name}          BuiltIn.Log
    Check Log Message     ${tc.body[1].body[0].body[0]}            start_keyword
    Check Log Message     ${tc.body[1].body[1]}                    Test 1
    Should Be Equal       ${tc.body[1].body[2].full_name}          BuiltIn.Log
    Check Log Message     ${tc.body[1].body[2].body[0]}            end_keyword
    Length Should Be      ${tc.body[1].body}                       3

In start_keyword and end_keyword with user keyword
    ${tc} =               Check Test Case                          First One
    Should Be Equal       ${tc.body[3].full_name}                  logs on trace
    Should Be Equal       ${tc.body[3].body[0].full_name}          BuiltIn.Log
    Check Log Message     ${tc.body[3].body[0].body[0]}            start_keyword
    Should Be Equal       ${tc.body[3].body[1].full_name}          BuiltIn.Log
    Should Be Equal       ${tc.body[3].body[1].body[0].full_name}  BuiltIn.Log
    Check Log Message     ${tc.body[3].body[1].body[0].body[0]}    start_keyword
    Should Be Equal       ${tc.body[3].body[1].body[1].full_name}  BuiltIn.Log
    Check Log Message     ${tc.body[3].body[1].body[1].body[0]}    end_keyword
    Length Should Be      ${tc.body[3].body[1].body}               2
    Should Be Equal       ${tc.body[3].body[2].full_name}          BuiltIn.Log
    Check Log Message     ${tc.body[3].body[2].body[0]}            end_keyword
    Length Should Be      ${tc.body[3].body}                       3

In start_keyword and end_keyword with FOR loop
    ${tc} =               Check Test Case                          FOR
    ${for} =              Set Variable                             ${tc.body[1]}
    Should Be Equal       ${for.type}                              FOR
    Length Should Be      ${for.body}                              5
    Length Should Be      ${for.body.filter(keywords=True)}        2
    Should Be Equal       ${for.body[0].full_name}                 BuiltIn.Log
    Check Log Message     ${for.body[0].body[0]}                   start_keyword
    Should Be Equal       ${for.body[-1].full_name}                BuiltIn.Log
    Check Log Message     ${for.body[-1].body[0]}                  end_keyword

In start_keyword and end_keyword with WHILE
    ${tc} =               Check Test Case                          While loop executed multiple times
    ${while} =            Set Variable                             ${tc.body[2]}
    Should Be Equal       ${while.type}                            WHILE
    Length Should Be      ${while.body}                            7
    Length Should Be      ${while.body.filter(keywords=True)}      2
    Should Be Equal       ${while.body[0].full_name}               BuiltIn.Log
    Check Log Message     ${while.body[0].body[0]}                 start_keyword
    Should Be Equal       ${while.body[-1].full_name}              BuiltIn.Log
    Check Log Message     ${while.body[-1].body[0]}                end_keyword

 In start_keyword and end_keyword with IF/ELSE
    ${tc} =               Check Test Case                          IF structure
    Should Be Equal       ${tc.body[1].type}                       VAR
    Should Be Equal       ${tc.body[2].type}                       IF/ELSE ROOT
    Length Should Be      ${tc.body[2].body}                       3                     # Listener is not called with root
    Validate IF branch    ${tc.body[2].body[0]}                    IF         NOT RUN    # but is called with unexecuted branches.
    Validate IF branch    ${tc.body[2].body[1]}                    ELSE IF    PASS
    Validate IF branch    ${tc.body[2].body[2]}                    ELSE       NOT RUN

In start_keyword and end_keyword with TRY/EXCEPT
    ${tc} =               Check Test Case                          Everything
    Should Be Equal       ${tc.body[1].type}                       TRY/EXCEPT ROOT
    Length Should Be      ${tc.body[1].body}                       5                     # Listener is not called with root
    Validate FOR branch   ${tc.body[1].body[0]}                    TRY        FAIL
    Validate FOR branch   ${tc.body[1].body[1]}                    EXCEPT     NOT RUN    # but is called with unexecuted branches.
    Validate FOR branch   ${tc.body[1].body[2]}                    EXCEPT     PASS
    Validate FOR branch   ${tc.body[1].body[3]}                    ELSE       NOT RUN
    Validate FOR branch   ${tc.body[1].body[4]}                    FINALLY    PASS

In start_keyword and end_keyword with BREAK and CONTINUE
    ${tc} =                   Check Test Case                                    WHILE loop in keyword
    FOR    ${iter}     IN     @{tc.body[1].body[2].body[1:-1]}
        Should Be Equal       ${iter.body[3].body[0].body[1].type}               CONTINUE
        Should Be Equal       ${iter.body[3].body[0].body[1].body[0].full_name}  BuiltIn.Log
        Check Log Message     ${iter.body[3].body[0].body[1].body[0].body[0]}    start_keyword
        Should Be Equal       ${iter.body[3].body[0].body[1].body[1].full_name}  BuiltIn.Log
        Check Log Message     ${iter.body[3].body[0].body[1].body[1].body[0]}    end_keyword
        Should Be Equal       ${iter.body[4].body[0].body[1].type}               BREAK
        Should Be Equal       ${iter.body[4].body[0].body[1].body[0].full_name}  BuiltIn.Log
        Check Log Message     ${iter.body[4].body[0].body[1].body[0].body[0]}    start_keyword
        Should Be Equal       ${iter.body[4].body[0].body[1].body[1].full_name}  BuiltIn.Log
        Check Log Message     ${iter.body[4].body[0].body[1].body[1].body[0]}    end_keyword
    END

In start_keyword and end_keyword with RETURN
    ${tc} =               Check Test Case                                          Second One
    Should Be Equal       ${tc.body[3].body[1].body[1].body[2].type}               RETURN
    Should Be Equal       ${tc.body[3].body[1].body[1].body[2].body[0].full_name}  BuiltIn.Log
    Check Log Message     ${tc.body[3].body[1].body[1].body[2].body[0].body[0]}    start_keyword
    Should Be Equal       ${tc.body[3].body[1].body[1].body[2].body[1].full_name}  BuiltIn.Log
    Check Log Message     ${tc.body[3].body[1].body[1].body[2].body[1].body[0]}    end_keyword

*** Keywords ***
Run Tests With Keyword Running Listener
    ${path} =    Normalize Path    ${LISTENER DIR}/keyword_running_listener.py
    ${files} =    Catenate
    ...    misc/normal.robot
    ...    misc/setups_and_teardowns.robot
    ...    misc/for_loops.robot
    ...    misc/while.robot
    ...    misc/if_else.robot
    ...    misc/try_except.robot
    Run Tests    --listener ${path}    ${files}    validate output=True
    Should Be Empty    ${ERRORS}

Validate IF branch
    [Arguments]    ${branch}    ${type}    ${status}
    Should Be Equal       ${branch.type}                           ${type}
    Should Be Equal       ${branch.status}                         ${status}
    Length Should Be      ${branch.body}                           3
    Should Be Equal       ${branch.body[0].full_name}              BuiltIn.Log
    Check Log Message     ${branch.body[0].body[0]}                start_keyword
    IF    $status == 'PASS'
        Should Be Equal       ${branch.body[1].full_name}              BuiltIn.Log
        Should Be Equal       ${branch.body[1].body[0].full_name}      BuiltIn.Log
        Check Log Message     ${branch.body[1].body[0].body[0]}        start_keyword
        Check Log Message     ${branch.body[1].body[1]}                else if branch
        Should Be Equal       ${branch.body[1].body[2].full_name}      BuiltIn.Log
        Check Log Message     ${branch.body[1].body[2].body[0]}        end_keyword
    ELSE
        Should Be Equal       ${branch.body[1].full_name}              BuiltIn.Fail
        Should Be Equal       ${branch.body[1].status}                 NOT RUN
    END
    Should Be Equal       ${branch.body[-1].full_name}             BuiltIn.Log
    Check Log Message     ${branch.body[-1].body[0]}               end_keyword

Validate FOR branch
    [Arguments]    ${branch}    ${type}    ${status}
    Should Be Equal       ${branch.type}                           ${type}
    Should Be Equal       ${branch.status}                         ${status}
    Should Be Equal       ${branch.body[0].full_name}              BuiltIn.Log
    Check Log Message     ${branch.body[0].body[0]}                start_keyword
    Should Be Equal       ${branch.body[-1].full_name}             BuiltIn.Log
    Check Log Message     ${branch.body[-1].body[0]}               end_keyword
