*** Settings ***
Suite Setup               Run Tests With Keyword Running Listener
Resource                  listener_resource.robot

*** Test Cases ***
In start_suite when suite has no setup
    Check Keyword Data    ${SUITE.setup}             Implicit setup    type=SETUP         children=1
    Validate Log          ${SUITE.setup[0]}          start_suite

In end_suite when suite has no teardown
    Check Keyword Data    ${SUITE.teardown}          Implicit teardown    type=TEARDOWN         children=1
    Validate Log          ${SUITE.teardown[0]}       end_suite

In start_suite when suite has setup
    VAR                   ${kw}                      ${SUITE.suites[1].setup}
    Check Keyword Data    ${kw}                      Suite Setup          type=SETUP            children=5
    Validate Log          ${kw[0]}                   start_suite
    Check Keyword Data    ${kw[1]}                   BuiltIn.Log          args=start_keyword    children=1
    Check Log Message     ${kw[1, 0]}                start_keyword
    Validate Log          ${kw[2]}                   Keyword
    Check Keyword Data    ${kw[3]}                   Keyword                                    children=3
    Check Keyword Data    ${kw[3, 0]}                BuiltIn.Log          args=start_keyword    children=1
    Check Log Message     ${kw[3, 0, 0]}             start_keyword
    Check Keyword Data    ${kw[3, 1]}                BuiltIn.Log          args=Keyword          children=3
    Check Keyword Data    ${kw[3, 2]}                BuiltIn.Log          args=end_keyword      children=1
    Check Log Message     ${kw[3, 2, 0]}             end_keyword
    Check Keyword Data    ${kw[4]}                   BuiltIn.Log          args=end_keyword      children=1
    Check Log Message     ${kw[4, 0]}                end_keyword

In end_suite when suite has teardown
    VAR                   ${kw}                      ${SUITE.suites[1].teardown}
    Check Keyword Data    ${kw}                      Suite Teardown       type=TEARDOWN         children=5
    Check Keyword Data    ${kw[0]}                   BuiltIn.Log          args=start_keyword    children=1
    Check Log Message     ${kw[0, 0]}                start_keyword
    Validate Log          ${kw[1]}                   Keyword
    Check Keyword Data    ${kw[2]}                   Keyword                                    children=3
    Check Keyword Data    ${kw[2, 0]}                BuiltIn.Log          args=start_keyword    children=1
    Check Log Message     ${kw[2, 0, 0]}             start_keyword
    Check Keyword Data    ${kw[2, 1]}                BuiltIn.Log          args=Keyword          children=3
    Check Keyword Data    ${kw[2, 2]}                BuiltIn.Log          args=end_keyword      children=1
    Check Log Message     ${kw[2, 2, 0]}             end_keyword
    Check Keyword Data    ${kw[3]}                   BuiltIn.Log          args=end_keyword      children=1
    Check Log Message     ${kw[3, 0]}                end_keyword
    Validate Log          ${kw[4]}                   end_suite

In start_test and end_test when test has no setup or teardown
    ${tc} =               Check Test Case                  First One
    Length Should Be      ${tc.body}                       5
    Should Not Be True    ${tc.setup}
    Should Not Be True    ${tc.teardown}
    Validate Log          ${tc[0]}                    start_test
    Validate Log          ${tc[1]}                    Test 1
    Validate Log          ${tc[2]}                    Logging with debug level    DEBUG
    Check Keyword Data    ${tc[3]}                    logs on trace    tags=kw, tags                   children=3
    Check Keyword Data    ${tc[3, 0]}                 BuiltIn.Log  args=start_keyword                  children=1
    Check Keyword Data    ${tc[3, 1]}                 BuiltIn.Log  args=Log on \${TEST NAME}, TRACE    children=3
    Check Keyword Data    ${tc[3, 2]}                 BuiltIn.Log  args=end_keyword                    children=1
    Validate Log          ${tc[4]}                    end_test

In start_test and end_test when test has setup and teardown
    ${tc} =               Check Test Case             Test with setup and teardown
    Length Should Be      ${tc.body}                  3
    Check Keyword Data    ${tc.setup}                 Test Setup           type=SETUP            children=4
    Check Keyword Data    ${tc.teardown}              Test Teardown        type=TEARDOWN         children=4
    Validate Log          ${tc[0]}                    start_test
    Check Keyword Data    ${tc[1]}                    Keyword                                    children=3
    Check Keyword Data    ${tc[1, 0]}                 BuiltIn.Log          args=start_keyword    children=1
    Check Log Message     ${tc[1, 0, 0]}              start_keyword
    Check Keyword Data    ${tc[1, 1]}                 BuiltIn.Log          args=Keyword          children=3
    Check Keyword Data    ${tc[1, 2]}                 BuiltIn.Log          args=end_keyword      children=1
    Check Log Message     ${tc[1, 2, 0]}              end_keyword
    Validate Log          ${tc[2]}                    end_test

In start_keyword and end_keyword with library keyword
    ${tc} =               Check Test Case             First One
    Should Be Equal       ${tc[1].full_name}          BuiltIn.Log
    Should Be Equal       ${tc[1, 0].full_name}       BuiltIn.Log
    Check Log Message     ${tc[1, 0, 0]}              start_keyword
    Check Log Message     ${tc[1, 1]}                 Test 1
    Should Be Equal       ${tc[1, 2].full_name}       BuiltIn.Log
    Check Log Message     ${tc[1, 2, 0]}              end_keyword
    Length Should Be      ${tc[1].body}               3

In start_keyword and end_keyword with user keyword
    ${tc} =               Check Test Case             First One
    Should Be Equal       ${tc[3].full_name}          logs on trace
    Should Be Equal       ${tc[3, 0].full_name}       BuiltIn.Log
    Check Log Message     ${tc[3, 0, 0]}              start_keyword
    Should Be Equal       ${tc[3, 1].full_name}       BuiltIn.Log
    Should Be Equal       ${tc[3, 1, 0].full_name}    BuiltIn.Log
    Check Log Message     ${tc[3, 1, 0, 1]}           start_keyword
    Should Be Equal       ${tc[3, 1, 2].full_name}    BuiltIn.Log
    Check Log Message     ${tc[3, 1, 2, 1]}           end_keyword
    Length Should Be      ${tc[3, 1].body}            3
    Should Be Equal       ${tc[3, 2].full_name}       BuiltIn.Log
    Check Log Message     ${tc[3, 2, 0]}              end_keyword
    Length Should Be      ${tc[3].body}               3

In start_keyword and end_keyword with FOR loop
    ${tc} =               Check Test Case                      FOR
    ${for} =              Set Variable                         ${tc[1]}
    Should Be Equal       ${for.type}                          FOR
    Length Should Be      ${for.body}                          5
    Length Should Be      ${for.body.filter(keywords=True)}    2
    Should Be Equal       ${for[0].full_name}                  BuiltIn.Log
    Check Log Message     ${for[0, 0]}                         start_keyword
    Should Be Equal       ${for[-1].full_name}                 BuiltIn.Log
    Check Log Message     ${for[-1,0]}                         end_keyword

In start_keyword and end_keyword with WHILE
    ${tc} =               Check Test Case                        While loop executed multiple times
    ${while} =            Set Variable                           ${tc[2]}
    Should Be Equal       ${while.type}                          WHILE
    Length Should Be      ${while.body}                          7
    Length Should Be      ${while.body.filter(keywords=True)}    2
    Should Be Equal       ${while[0].full_name}                  BuiltIn.Log
    Check Log Message     ${while[0, 0]}                         start_keyword
    Should Be Equal       ${while[-1].full_name}                 BuiltIn.Log
    Check Log Message     ${while[-1,0]}                         end_keyword

In start_keyword and end_keyword with IF/ELSE
    ${tc} =               Check Test Case                IF structure
    Should Be Equal       ${tc[1].type}                  VAR
    Should Be Equal       ${tc[2].type}                  IF/ELSE ROOT
    Length Should Be      ${tc[2].body}                  3                     # Listener is not called with root
    Validate IF branch    ${tc[2, 0]}                    IF         NOT RUN    # but is called with unexecuted branches.
    Validate IF branch    ${tc[2, 1]}                    ELSE IF    PASS
    Validate IF branch    ${tc[2, 2]}                    ELSE       NOT RUN

In start_keyword and end_keyword with TRY/EXCEPT
    ${tc} =               Check Test Case                Everything
    Should Be Equal       ${tc[1].type}                  TRY/EXCEPT ROOT
    Length Should Be      ${tc[1].body}                  5                     # Listener is not called with root
    Validate FOR branch   ${tc[1, 0]}                    TRY        FAIL
    Validate FOR branch   ${tc[1, 1]}                    EXCEPT     NOT RUN    # but is called with unexecuted branches.
    Validate FOR branch   ${tc[1, 2]}                    EXCEPT     PASS
    Validate FOR branch   ${tc[1, 3]}                    ELSE       NOT RUN
    Validate FOR branch   ${tc[1, 4]}                    FINALLY    PASS

In start_keyword and end_keyword with BREAK and CONTINUE
    ${tc} =                   Check Test Case                  WHILE loop in keyword
    FOR    ${iter}     IN     @{tc[1, 2][1:-1]}
        Should Be Equal       ${iter[3, 0, 1].type}            CONTINUE
        Should Be Equal       ${iter[3, 0, 1, 0].full_name}    BuiltIn.Log
        Check Log Message     ${iter[3, 0, 1, 0, 0]}           start_keyword
        Should Be Equal       ${iter[3, 0, 1, 1].full_name}    BuiltIn.Log
        Check Log Message     ${iter[3, 0, 1, 1, 0]}           end_keyword
        Should Be Equal       ${iter[4, 0, 1].type}            BREAK
        Should Be Equal       ${iter[4, 0, 1, 0].full_name}    BuiltIn.Log
        Check Log Message     ${iter[4, 0, 1, 0, 0]}           start_keyword
        Should Be Equal       ${iter[4, 0, 1, 1].full_name}    BuiltIn.Log
        Check Log Message     ${iter[4, 0, 1, 1, 0]}           end_keyword
    END

In start_keyword and end_keyword with RETURN
    ${tc} =               Check Test Case                      Second One
    Should Be Equal       ${tc[3, 1, 1, 2].type}               RETURN
    Should Be Equal       ${tc[3, 1, 1, 2, 0].full_name}       BuiltIn.Log
    Check Log Message     ${tc[3, 1, 1, 2, 0, 1]}              start_keyword
    Should Be Equal       ${tc[3, 1, 1, 2, 1].full_name}       BuiltIn.Log
    Check Log Message     ${tc[3, 1, 1, 2, 1, 1]}              end_keyword

In dry-run
    Run Tests With Keyword Running Listener    --dry-run
    Should Contain Tests    ${SUITE}
    ...    First One
    ...    Test with setup and teardown
    ...    FOR
    ...    FOR IN ENUMERATE
    ...    FOR IN ZIP
    ...    WHILE loop executed multiple times
    ...    WHILE loop in keyword
    ...    IF structure
    ...    Everything
    ...    Second One=FAIL:Several failures occurred:\n\n1) No keyword with name 'Not executed' found.\n\n2) No keyword with name 'Not executed' found.
    ...    Test with failing setup=PASS
    ...    Test with failing teardown=PASS
    ...    Failing test with failing teardown=PASS
    ...    FOR IN RANGE=FAIL:No keyword with name 'Not executed!' found.

*** Keywords ***
Run Tests With Keyword Running Listener
    [Arguments]    ${options}=
    ${path} =    Normalize Path    ${LISTENER DIR}/keyword_running_listener.py
    ${files} =    Catenate
    ...    misc/normal.robot
    ...    misc/setups_and_teardowns.robot
    ...    misc/for_loops.robot
    ...    misc/while.robot
    ...    misc/if_else.robot
    ...    misc/try_except.robot
    Run Tests    --listener ${path} ${options} -L debug    ${files}    validate output=True
    Should Be Empty    ${ERRORS}

Validate Log
    [Arguments]    ${kw}    ${message}    ${level}=INFO
    IF    $level == 'INFO'
        VAR    ${args}    ${message}
    ELSE
        VAR    ${args}    ${message}, ${level}
    END
    Check Keyword Data    ${kw}              BuiltIn.Log    args=${args}          children=3
    Check Keyword Data    ${kw[0]}           BuiltIn.Log    args=start_keyword    children=1
    Check Log Message     ${kw[0, 0]}        start_keyword
    Check Log Message     ${kw[1]}           ${message}     ${level}
    Check Keyword Data    ${kw[2]}           BuiltIn.Log    args=end_keyword      children=1
    Check Log Message     ${kw[2, 0]}        end_keyword

Validate IF branch
    [Arguments]    ${branch}    ${type}    ${status}
    Should Be Equal       ${branch.type}                 ${type}
    Should Be Equal       ${branch.status}               ${status}
    Length Should Be      ${branch.body}                 3
    Should Be Equal       ${branch[0].full_name}         BuiltIn.Log
    Check Log Message     ${branch[0, 0]}                start_keyword
    IF    $status == 'PASS'
        Should Be Equal       ${branch[1].full_name}       BuiltIn.Log
        Should Be Equal       ${branch[1, 0].full_name}    BuiltIn.Log
        Check Log Message     ${branch[1, 0, 0]}           start_keyword
        Check Log Message     ${branch[1, 1]}              else if branch
        Should Be Equal       ${branch[1, 2].full_name}    BuiltIn.Log
        Check Log Message     ${branch[1, 2, 0]}           end_keyword
    ELSE
        Should Be Equal       ${branch[1].full_name}       BuiltIn.Fail
        Should Be Equal       ${branch[1].status}          NOT RUN
    END
    Should Be Equal       ${branch[-1].full_name}          BuiltIn.Log
    Check Log Message     ${branch[-1,0]}                  end_keyword

Validate FOR branch
    [Arguments]    ${branch}    ${type}    ${status}
    Should Be Equal       ${branch.type}               ${type}
    Should Be Equal       ${branch.status}             ${status}
    Should Be Equal       ${branch[0].full_name}       BuiltIn.Log
    Check Log Message     ${branch[0, 0]}              start_keyword
    Should Be Equal       ${branch[-1].full_name}      BuiltIn.Log
    Check Log Message     ${branch[-1,0]}              end_keyword
