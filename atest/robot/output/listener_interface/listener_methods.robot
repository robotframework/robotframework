*** Settings ***
Suite Setup       Run Tests With Listeners
Suite Teardown    Remove Listener Files
Resource          listener_resource.robot

*** Test Cases ***
Listen All
    [Documentation]    Listener listening all methods. Method names with underscore.
    Check Listen All File    ${ALL_FILE}

Listen All With Arguments To Listener
    Check Listen All File    ${ALL_FILE2}

Listen All Module Listener
    Check Listen All File    ${MODULE_FILE}

Listen Some
    [Documentation]    Only listening some methods. Method names with camelCase.
    @{expected} =    Create List    Pass    Fail    ${SUITE_MSG}
    Check Listener File    ${SOME_FILE}    @{expected}

Correct Attributes To Listener Methods
    ${status} =    Log File    %{TEMPDIR}/${ATTR_TYPE_FILE}
    Stderr Should Not Contain    attributeverifyinglistener
    Should Not Contain    ${status}    FAILED

Keyword Tags
    ${status} =    Log File    %{TEMPDIR}/${ATTR_TYPE_FILE}
    Should Contain X Times    ${status}    PASSED | tags: [force, keyword, tags]    6

Suite And Test Counts
    Run Tests    --listener listeners.SuiteAndTestCounts    misc/suites/subsuites misc/suites/subsuites2
    Stderr Should Be Empty

Suite Source
    Run Tests    --listener listeners.SuiteSource --name Root    misc/suites/subsuites misc/pass_and_fail.robot
    Stderr Should Be Empty

Keyword Type
    Run Tests    --listener listeners.KeywordType    misc/setups_and_teardowns.robot misc/for_loops.robot misc/if_else.robot
    Stderr Should Be Empty

Keyword Status
    Run Tests    --listener listeners.KeywordStatus    misc/pass_and_fail.robot misc/if_else.robot
    Stderr Should Be Empty

Executing Keywords from Listeners
    Run Tests    --listener listeners.KeywordExecutingListener    misc/pass_and_fail.robot
    ${tc}=    Get Test Case    Pass
    Check Log Message    ${tc.kws[0].msgs[0]}    Start Pass
    Check Log Message    ${tc.kws[2].msgs[0]}    End Pass

Test Template
    ${listener} =    Normalize Path    ${LISTENER DIR}/verify_template_listener.py
    Run Tests    --listener ${listener}    ${LISTENER DIR}/test_template.robot
    Stderr Should Be Empty

Keyword Arguments Are Always Strings
    ${result} =    Run Tests    --listener attributeverifyinglistener    ${LISTENER DIR}/keyword_argument_types.robot
    Should Be Empty    ${result.stderr}
    Check Test Tags    Run Keyword with already resolved non-string arguments in test data    1    2
    Check Test Case    Run Keyword with non-string arguments in library
    ${status} =    Log File    %{TEMPDIR}/${ATTR_TYPE_FILE}
    Should Not Contain    ${status}    FAILED

TimeoutError occurring during listener method is propagaged
    [Documentation]    Timeouts can only occur inside `log_message`.
    ...    Cannot reliable set timeouts to occur during it, so the listener
    ...    emulates the situation by explicitly raising TimeoutError.
    Run Tests    --listener ${LISTENER DIR}/timeouting_listener.py    ${LISTENER DIR}/timeouting_listener.robot
    Check Test Case    Timeout in test case level
    Check Test Case    Timeout inside user keyword
    Stderr Should Be Empty

*** Keywords ***
Run Tests With Listeners
    ${args} =    Join Command Line
    ...    --listener    ListenAll
    ...    --listener    ListenAll:%{TEMPDIR}${/}${ALL_FILE2}
    ...    --listener    module_listener
    ...    --listener    listeners.ListenSome
    ...    --listener    attributeverifyinglistener
    ...    --metadata    ListenerMeta:Hello
    Run Tests    ${args}    misc/pass_and_fail.robot

Check Listen All File
    [Arguments]    ${filename}
    @{expected}=    Create List    Got settings on level: INFO
    ...    SUITE START: Pass And Fail (s1) 'Some tests here' [ListenerMeta: Hello]
    ...    SETUP START: My Keyword ['Suite Setup'] (line 3)
    ...    KEYWORD START: BuiltIn.Log ['Hello says "\${who}"!', '\${LEVEL1}'] (line 27)
    ...    LOG MESSAGE: [INFO] Hello says "Suite Setup"!
    ...    KEYWORD END: PASS
    ...    KEYWORD START: BuiltIn.Log ['Debug message', '\${LEVEL2}'] (line 28)
    ...    KEYWORD END: PASS
    ...    KEYWORD START: \${assign} = String.Convert To Upper Case ['Just testing...'] (line 29)
    ...    LOG MESSAGE: [INFO] \${assign} = JUST TESTING...
    ...    KEYWORD END: PASS
    ...    SETUP END: PASS
    ...    TEST START: Pass (s1-t1, line 12) '' ['force', 'pass']
    ...    KEYWORD START: My Keyword ['Pass'] (line 15)
    ...    KEYWORD START: BuiltIn.Log ['Hello says "\${who}"!', '\${LEVEL1}'] (line 27)
    ...    LOG MESSAGE: [INFO] Hello says "Pass"!
    ...    KEYWORD END: PASS
    ...    KEYWORD START: BuiltIn.Log ['Debug message', '\${LEVEL2}'] (line 28)
    ...    KEYWORD END: PASS
    ...    KEYWORD START: \${assign} = String.Convert To Upper Case ['Just testing...'] (line 29)
    ...    LOG MESSAGE: [INFO] \${assign} = JUST TESTING...
    ...    KEYWORD END: PASS
    ...    KEYWORD END: PASS
    ...    TEST END: PASS
    ...    TEST START: Fail (s1-t2, line 17) 'FAIL Expected failure' ['fail', 'force']
    ...    KEYWORD START: My Keyword ['Fail'] (line 20)
    ...    KEYWORD START: BuiltIn.Log ['Hello says "\${who}"!', '\${LEVEL1}'] (line 27)
    ...    LOG MESSAGE: [INFO] Hello says "Fail"!
    ...    KEYWORD END: PASS
    ...    KEYWORD START: BuiltIn.Log ['Debug message', '\${LEVEL2}'] (line 28)
    ...    KEYWORD END: PASS
    ...    KEYWORD START: \${assign} = String.Convert To Upper Case ['Just testing...'] (line 29)
    ...    LOG MESSAGE: [INFO] \${assign} = JUST TESTING...
    ...    KEYWORD END: PASS
    ...    KEYWORD END: PASS
    ...    KEYWORD START: BuiltIn.Fail ['Expected failure'] (line 21)
    ...    LOG MESSAGE: [FAIL] Expected failure
    ...    KEYWORD END: FAIL
    ...    TEST END: FAIL Expected failure
    ...    SUITE END: FAIL 2 tests, 1 passed, 1 failed
    ...    Output: output.xml    Closing...
    Check Listener File    ${filename}    @{expected}

Calling listener failed
    [Arguments]    ${method}    ${error}
    Stderr Should Contain    [ ERROR ] Calling listener method '${method}' of
    ...    listener 'listeners.InvalidMethods' failed: ${error}
