*** Settings ***
Suite Setup       Run Tests With Listeners
Suite Teardown    Remove Listener Files
Resource          listener_resource.robot

*** Variables ***
${LISTENER DIR}   ${DATADIR}/output/listeners

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

Java Listener
    [Documentation]    Listener listening all methods implemented with Java
    [Tags]    require-jython
    @{expected} =    Create List    Got settings on level: INFO
    ...    START SUITE: Pass And Fail 'Some tests here' [ListenerMeta: Hello]
    ...    START KW: My Keyword [Suite Setup]
    ...    START KW: BuiltIn.Log [Hello says "\${who}"!\${LEVEL1}]
    ...    LOG MESSAGE: [INFO] Hello says "Suite Setup"!
    ...    START KW: BuiltIn.Log [Debug message\${LEVEL2}]
    ...    START KW: String.Convert To Upper Case [Just testing...]
    ...    LOG MESSAGE: [INFO] \${assign} = JUST TESTING...
    ...    START TEST: Pass '' [forcepass]
    ...    START KW: My Keyword [Pass]
    ...    START KW: BuiltIn.Log [Hello says "\${who}"!\${LEVEL1}]
    ...    LOG MESSAGE: [INFO] Hello says "Pass"!
    ...    START KW: BuiltIn.Log [Debug message\${LEVEL2}]
    ...    START KW: String.Convert To Upper Case [Just testing...]
    ...    LOG MESSAGE: [INFO] \${assign} = JUST TESTING...
    ...    END TEST: PASS
    ...    START TEST: Fail 'FAIL Expected failure' [failforce]
    ...    START KW: My Keyword [Fail]
    ...    START KW: BuiltIn.Log [Hello says "\${who}"!\${LEVEL1}]
    ...    LOG MESSAGE: [INFO] Hello says "Fail"!
    ...    START KW: BuiltIn.Log [Debug message\${LEVEL2}]
    ...    START KW: String.Convert To Upper Case [Just testing...]
    ...    LOG MESSAGE: [INFO] \${assign} = JUST TESTING...
    ...    START KW: BuiltIn.Fail [Expected failure]
    ...    LOG MESSAGE: [FAIL] Expected failure
    ...    END TEST: FAIL: Expected failure
    ...    END SUITE: FAIL: 2 tests, 1 passed, 1 failed
    ...    Output (java): output.xml    The End
    Check Listener File    ${JAVA_FILE}    @{expected}

Correct Attributes To Listener Methods
    ${status} =    Log File    %{TEMPDIR}/${ATTR_TYPE_FILE}
    Stderr Should Not Contain    attributeverifyinglistener
    Should Not Contain    ${status}    FAILED

Correct Attributes To Java Listener Methods
    [Tags]    require-jython
    ${status} =    Log File    %{TEMPDIR}/${JAVA_ATTR_TYPE_FILE}
    Stderr Should Not Contain    JavaAttributeVerifyingListener
    Should Not Contain    ${status}    FAILED

Keyword Tags
    ${status} =    Log File    %{TEMPDIR}/${ATTR_TYPE_FILE}
    Should Contain X Times    ${status}    PASSED | tags: [force, keyword, tags]    6

FOR and IF line numbers
    Run Tests    --listener ListenAll    misc/for_loops.robot misc/if_else.robot
    Stderr Should Be Empty
    ${output} =    Get Listener File    ${ALL FILE}
    FOR    ${expected}    IN
    ...    FOR START: \${pet} IN [ cat | dog | horse ] (for_loops.robot:3)
    ...    FOR ITEM START: \${pet} = cat (for_loops.robot:3)
    ...    KW START: BuiltIn.Log ['\${pet}'] (for_loops.robot:4)
    ...    FOR ITEM START: \${pet} = dog (for_loops.robot:3)
    ...    KW START: BuiltIn.Log ['\${pet}'] (for_loops.robot:4)
    ...    IF START: 'IF' == 'WRONG' (if_else.robot:3)
    ...    IF END: NOT_RUN
    ...    ELSE IF START: 'ELSE IF' == 'ELSE IF' (if_else.robot:5)
    ...    KW START: BuiltIn.Log ['else if branch'] (if_else.robot:6)
    ...    ELSE IF END: PASS
    ...    ELSE START: (if_else.robot:7)
    ...    ELSE END: NOT_RUN
        Should Contain    ${output}    ${expected}
    END

Suite And Test Counts
    Run Tests    --listener listeners.SuiteAndTestCounts    misc/suites/subsuites misc/suites/subsuites2
    Stderr Should Be Empty

Suite Source
    Run Tests    --listener listeners.SuiteSource --name Root    misc/suites/subsuites misc/pass_and_fail.robot
    Stderr Should Be Empty

Keyword Type
    Run Tests    --listener listeners.KeywordType    misc/setups_and_teardowns.robot misc/for_loops.robot misc/if_else.robot
    Stderr Should Be Empty

Suite And Test Counts With Java
    [Tags]    require-jython
    Run Tests    --listener JavaSuiteAndTestCountListener    misc/suites/subsuites misc/suites/subsuites2
    Stderr Should Be Empty

Executing Keywords from Listeners
    Run Tests    --listener listeners.KeywordExecutingListener    misc/pass_and_fail.robot
    ${tc}=    Get Test Case    Pass
    Check Log Message    ${tc.kws[0].msgs[0]}    Start Pass
    Check Log Message    ${tc.kws[2].msgs[0]}    End Pass

Test Template
    ${listener} =    Normalize Path    ${DATADIR}/output/listeners/verify_template_listener.py
    File Should Exist    ${listener}
    Run Tests    --listener ${listener}    output/listeners/test_template.robot
    Stderr Should Be Empty

Keyword Arguments Are Always Strings
    ${result} =    Run Tests    --listener attributeverifyinglistener    output/listeners/keyword_argument_types.robot
    Should Be Empty    ${result.stderr}
    Check Test Tags    Run Keyword with already resolved non-string arguments in test data    1    2
    Check Test Case    Run Keyword with non-string arguments in library
    ${status} =    Log File    %{TEMPDIR}/${ATTR_TYPE_FILE}
    Should Not Contain    ${status}    FAILED

TimeoutError occurring during listener method is propagaged
    [Documentation]    Timeouts can only occur inside `log_message`.
    ...    Cannot reliable set timeouts to occur during it, so the listener
    ...    emulates the situation by explicitly raising TimeoutError.
    Run Tests    --listener ${LISTENER DIR}/timeouting_listener.py    output/listeners/timeouting_listener.robot
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
    ...    --listener    JavaListener
    ...    --listener    attributeverifyinglistener
    ...    --listener    JavaAttributeVerifyingListener
    ...    --metadata    ListenerMeta:Hello
    Run Tests    ${args}    misc/pass_and_fail.robot

Check Listen All File
    [Arguments]    ${filename}
    @{expected}=    Create List    Got settings on level: INFO
    ...    SUITE START: Pass And Fail (s1) 'Some tests here' [ListenerMeta: Hello]
    ...    SETUP START: My Keyword ['Suite Setup'] (pass_and_fail.robot:3)
    ...    KW START: BuiltIn.Log ['Hello says "\${who}"!', '\${LEVEL1}'] (pass_and_fail.robot:27)
    ...    LOG MESSAGE: [INFO] Hello says "Suite Setup"!
    ...    KW END: PASS
    ...    KW START: BuiltIn.Log ['Debug message', '\${LEVEL2}'] (pass_and_fail.robot:28)
    ...    KW END: PASS
    ...    KW START: \${assign} = String.Convert To Upper Case ['Just testing...'] (pass_and_fail.robot:29)
    ...    LOG MESSAGE: [INFO] \${assign} = JUST TESTING...
    ...    KW END: PASS
    ...    SETUP END: PASS
    ...    TEST START: Pass (s1-t1, line 12) '' ['force', 'pass']
    ...    KW START: My Keyword ['Pass'] (pass_and_fail.robot:15)
    ...    KW START: BuiltIn.Log ['Hello says "\${who}"!', '\${LEVEL1}'] (pass_and_fail.robot:27)
    ...    LOG MESSAGE: [INFO] Hello says "Pass"!
    ...    KW END: PASS
    ...    KW START: BuiltIn.Log ['Debug message', '\${LEVEL2}'] (pass_and_fail.robot:28)
    ...    KW END: PASS
    ...    KW START: \${assign} = String.Convert To Upper Case ['Just testing...'] (pass_and_fail.robot:29)
    ...    LOG MESSAGE: [INFO] \${assign} = JUST TESTING...
    ...    KW END: PASS
    ...    KW END: PASS
    ...    TEST END: PASS
    ...    TEST START: Fail (s1-t2, line 17) 'FAIL Expected failure' ['fail', 'force']
    ...    KW START: My Keyword ['Fail'] (pass_and_fail.robot:20)
    ...    KW START: BuiltIn.Log ['Hello says "\${who}"!', '\${LEVEL1}'] (pass_and_fail.robot:27)
    ...    LOG MESSAGE: [INFO] Hello says "Fail"!
    ...    KW END: PASS
    ...    KW START: BuiltIn.Log ['Debug message', '\${LEVEL2}'] (pass_and_fail.robot:28)
    ...    KW END: PASS
    ...    KW START: \${assign} = String.Convert To Upper Case ['Just testing...'] (pass_and_fail.robot:29)
    ...    LOG MESSAGE: [INFO] \${assign} = JUST TESTING...
    ...    KW END: PASS
    ...    KW END: PASS
    ...    KW START: BuiltIn.Fail ['Expected failure'] (pass_and_fail.robot:21)
    ...    LOG MESSAGE: [FAIL] Expected failure
    ...    KW END: FAIL
    ...    TEST END: FAIL Expected failure
    ...    SUITE END: FAIL 2 tests, 1 passed, 1 failed
    ...    Output: output.xml    Closing...
    Check Listener File    ${filename}    @{expected}

Calling listener failed
    [Arguments]    ${method}    ${error}
    Stderr Should Contain    [ ERROR ] Calling listener method '${method}' of
    ...    listener 'listeners.InvalidMethods' failed: ${error}
