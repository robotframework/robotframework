*** Settings ***
Suite Setup     Run Tests  --listener OldListenAll --listener OldListenAll:%{TEMPDIR}${/}${ALL_FILE2} --listener old_module_listener --listener old_listeners.ListenSome --listener OldJavaListener --listener old_listeners.InvalidMethods  misc/pass_and_fail.robot
Suite Teardown  Remove Listener Files
Resource        listener_resource.robot

*** Test Cases ***
Listen All
    [Documentation]  Listener listening all methods. Method names with underscore.
    Check Listen All File  ${ALL_FILE}

Listen All With Arguments to Listener
    Check Listen All File  ${ALL_FILE2}

Listen All Module Listener
    Check Listen All File  ${MODULE_FILE}

Listen Some
    [Documentation]  Only listening some methods. Method names with camelCase.
    @{expected} =  Create List  Pass  Fail  ${SUITE_MSG_2}
    Check Listener File  ${SOME_FILE}  @{expected}

Java Listener
    [Documentation]  Listener listening all methods implemented with Java
    [Tags]  require-jython
    @{expected} =  Create List
    ...  START SUITE: Pass And Fail 'Some tests here'
    ...  START KW: My Keyword [Suite Setup]
    ...  START KW: BuiltIn.Log [Hello says "\${who}"!\${LEVEL1}]
    ...  START KW: BuiltIn.Log [Debug message\${LEVEL2}]
    ...  START KW: BuiltIn.Set Variable [Just testing...]
    ...  START TEST: Pass '' [forcepass]
    ...  START KW: My Keyword [Pass]
    ...  START KW: BuiltIn.Log [Hello says "\${who}"!\${LEVEL1}]
    ...  START KW: BuiltIn.Log [Debug message\${LEVEL2}]
    ...  START KW: BuiltIn.Set Variable [Just testing...]
    ...  END TEST: PASS
    ...  START TEST: Fail 'FAIL Expected failure' [failforce]
    ...  START KW: My Keyword [Fail]
    ...  START KW: BuiltIn.Log [Hello says "\${who}"!\${LEVEL1}]
    ...  START KW: BuiltIn.Log [Debug message\${LEVEL2}]
    ...  START KW: BuiltIn.Set Variable [Just testing...]
    ...  START KW: BuiltIn.Fail [Expected failure]
    ...  END TEST: FAIL: Expected failure
    ...  END SUITE: FAIL: 2 critical tests, 1 passed, 1 failed  2 tests total, 1 passed, 1 failed
    ...  Output (java): output.xml
    ...  The End
    Check Listener File  ${JAVA_FILE}  @{expected}

Invalid Args For Listener Method
    Calling listener method failed  start_suite  TypeError: start_suite()

Listener Method Raising Exception
    Calling listener method failed  end_suite  Here comes an exception!

*** Keywords ***
Check Listen All File
    [Arguments]  ${filename}
    @{expected} =  Create List  SUITE START: Pass And Fail 'Some tests here'
    ...  KW START: My Keyword ['Suite Setup']
    ...  KW START: BuiltIn.Log ['Hello says "\${who}"!', '\${LEVEL1}']
    ...  KW END: PASS
    ...  KW START: BuiltIn.Log ['Debug message', '\${LEVEL2}']
    ...  KW END: PASS
    ...  KW START: BuiltIn.Set Variable ['Just testing...']
    ...  KW END: PASS
    ...  KW END: PASS
    ...  TEST START: Pass '' ['force', 'pass']
    ...  KW START: My Keyword ['Pass']
    ...  KW START: BuiltIn.Log ['Hello says "\${who}"!', '\${LEVEL1}']
    ...  KW END: PASS
    ...  KW START: BuiltIn.Log ['Debug message', '\${LEVEL2}']
    ...  KW END: PASS
    ...  KW START: BuiltIn.Set Variable ['Just testing...']
    ...  KW END: PASS
    ...  KW END: PASS
    ...  TEST END: PASS
    ...  TEST START: Fail 'FAIL Expected failure' ['fail', 'force']
    ...  KW START: My Keyword ['Fail']
    ...  KW START: BuiltIn.Log ['Hello says "\${who}"!', '\${LEVEL1}']
    ...  KW END: PASS
    ...  KW START: BuiltIn.Log ['Debug message', '\${LEVEL2}']
    ...  KW END: PASS
    ...  KW START: BuiltIn.Set Variable ['Just testing...']
    ...  KW END: PASS
    ...  KW END: PASS
    ...  KW START: BuiltIn.Fail ['Expected failure']
    ...  KW END: FAIL
    ...  TEST END: FAIL Expected failure
    ...  SUITE END: FAIL 2 critical tests, 1 passed, 1 failed  2 tests total, 1 passed, 1 failed
    ...  Output: output.xml
    ...  Closing...
    Check Listener File  ${filename}  @{expected}

Calling listener method failed
    [Arguments]  ${method}  ${error}
    Check Stderr Contains  [ ERROR ]  Calling listener method '${method}' of
    ...  listener 'old_listeners.InvalidMethods' failed:  ${error}
